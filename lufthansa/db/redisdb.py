# -*- coding: utf-8 -*-
"""
@author: boris and koala
"""
import time
import redis
from redis._compat import unicode, long, basestring
from redis.connection import Encoder as _Encoder
from redis.exceptions import ConnectionError, TimeoutError
from redis.exceptions import DataError
from redis.sentinel import Sentinel
from lufthansa.lufthansa.rediscluster.client import RedisCluster
# from lufthansa.lufthansa.settings_.setting import Settings
from lufthansa.lufthansa import settings
from loguru import logger


class Encoder(_Encoder):
    def encode(self, value):
        "Return a bytestring or bytes-like representation of the value"
        if isinstance(value, (bytes, memoryview)):
            return value
        # elif isinstance(value, bool):
        #     # special case bool since it is a subclass of int
        #     raise DataError(
        #         "Invalid input of type: 'bool'. Convert to a "
        #         "bytes, string, int or float first."
        #     )
        elif isinstance(value, float):
            value = repr(value).encode()
        elif isinstance(value, (int, long)):
            # python 2 repr() on longs is '123L', so use str() instead
            value = str(value).encode()
        elif isinstance(value, (list, dict, tuple)):
            value = unicode(value)
        elif not isinstance(value, basestring):
            # a value we don't know how to deal with. throw an error
            typename = type(value).__name__
            raise DataError(
                "Invalid input of type: '%s'. Convert to a "
                "bytes, string, int or float first." % typename
            )
        if isinstance(value, unicode):
            value = value.encode(self.encoding, self.encoding_errors)
        return value


redis.connection.Encoder = Encoder


class RedisDB:
    def __init__(
            self,
            ip_ports=None,
            db=None,
            user_pass=None,
            url=None,
            decode_responses=True,
            service_name=None,
            max_connections=32,
            **kwargs,
    ):
        """
        redis?????????
        Args:
            ip_ports: ip:port ??????????????????????????????????????? ??? ip1:port1,ip2:port2 ??? ["ip1:port1", "ip2:port2"]
            db:
            user_pass:
            url:
            decode_responses:
            service_name: ?????????redis????????????
        """

        # ????????????setting??????????????????????????????????????????????????????????????????????????????
        if ip_ports is None:
            ip_ports = settings.REDISDB_IP_PORTS
        if db is None:
            db = settings.REDISDB_DB
        if user_pass is None:
            user_pass = None #setting.REDISDB_USER_PASS
        if service_name is None:
            service_name = None # setting.REDISDB_SERVICE_NAME

        self._is_redis_cluster = False

        self.__redis = None
        self._url = url
        self._ip_ports = ip_ports
        self._db = db
        self._user_pass = user_pass
        self._decode_responses = decode_responses
        self._service_name = service_name
        self._max_connections = max_connections
        self._kwargs = kwargs
        self.get_connect()

    def __repr__(self):
        if self._url:
            return "<Redisdb url:{}>".format(self._url)

        return "<Redisdb ip_ports: {} db:{} user_pass:{}>".format(
            self._ip_ports, self._db, self._user_pass
        )

    @property
    def _redis(self):
        try:
            if not self.__redis.ping():
                raise ConnectionError("unable to connect to redis")
        except:
            self._reconnect()

        return self.__redis

    @_redis.setter
    def _redis(self, val):
        self.__redis = val

    def get_connect(self):
        # ?????????????????????
        try:
            if not self._url:
                if not self._ip_ports:
                    raise ConnectionError("????????? redis ????????????")

                ip_ports = (
                    self._ip_ports
                    if isinstance(self._ip_ports, list)
                    else self._ip_ports.split(",")
                )
                if len(ip_ports) > 1:
                    startup_nodes = []
                    for ip_port in ip_ports:
                        ip, port = ip_port.split(":")
                        startup_nodes.append({"host": ip, "port": port})

                    if self._service_name:
                        # logger.debug("??????redis????????????")
                        hosts = [(node["host"], node["port"]) for node in startup_nodes]
                        sentinel = Sentinel(hosts, socket_timeout=3, **self._kwargs)
                        self._redis = sentinel.master_for(
                            self._service_name,
                            password=self._user_pass,
                            db=self._db,
                            redis_class=redis.StrictRedis,
                            decode_responses=self._decode_responses,
                            max_connections=self._max_connections,
                            **self._kwargs,
                        )

                    else:
                        # logger.debug("??????redis????????????")
                        self._redis = RedisCluster(
                            startup_nodes=startup_nodes,
                            decode_responses=self._decode_responses,
                            password=self._user_pass,
                            max_connections=self._max_connections,
                            **self._kwargs,
                        )

                    self._is_redis_cluster = True
                else:
                    ip, port = ip_ports[0].split(":")
                    self._redis = redis.StrictRedis(
                        host=ip,
                        port=port,
                        db=self._db,
                        password=self._user_pass,
                        decode_responses=self._decode_responses,
                        max_connections=self._max_connections,
                        **self._kwargs,
                    )
                    self._is_redis_cluster = False
            else:
                self._redis = redis.StrictRedis.from_url(
                    self._url, decode_responses=self._decode_responses
                )
                self._is_redis_cluster = False

        except Exception as e:
            raise e

        # ????????????self._redis.ping() ?????????????????????
        return self.__redis.ping()

    @classmethod
    def from_url(cls, url):
        """

        Args:
            url: redis://[[username]:[password]]@[host]:[port]/[db]

        Returns:

        """
        return cls(url=url)

    def sadd(self, table, values):
        """
        @summary: ????????????set????????????????????? ??????
        ---------
        @param table:
        @param values: ?????? ??????list ??? ?????????
        ---------
        @result: ??????????????? ??????0????????????????????????1??? ??????????????????None
        """

        if isinstance(values, list):
            pipe = self._redis.pipeline()

            if not self._is_redis_cluster:
                pipe.multi()
            for value in values:
                pipe.sadd(table, value)
            pipe.execute()

        else:
            return self._redis.sadd(table, values)

    def sget(self, table, count=1, is_pop=True):
        """
        ?????? list ??? ['1'] ??? []
        @param table:
        @param count:
        @param is_pop:
        @return:
        """

        datas = []
        if is_pop:
            count = count if count <= self.sget_count(table) else self.sget_count(table)
            if count:
                if count > 1:
                    pipe = self._redis.pipeline()

                    if not self._is_redis_cluster:
                        pipe.multi()
                    while count:
                        pipe.spop(table)
                        count -= 1
                    datas = pipe.execute()

                else:
                    datas.append(self._redis.spop(table))

        else:
            datas = self._redis.srandmember(table, count)

        return datas

    def srem(self, table, values):
        """
        @summary: ??????????????????????????????
        ---------
        @param table:
        @param values: ??????????????????
        ---------
        @result:
        """

        if isinstance(values, list):
            pipe = self._redis.pipeline()

            if not self._is_redis_cluster:
                pipe.multi()
            for value in values:
                pipe.srem(table, value)
            pipe.execute()
        else:
            self._redis.srem(table, values)

    def sget_count(self, table):
        return self._redis.scard(table)

    def sdelete(self, table):
        """
        @summary: ??????set???????????????????????????????????????
        ?????????set????????????sscan??????????????????????????????500??????????????????srem???????????????????????????
        ????????????delete??????????????????Redis????????????????????????????????????????????????????????????
        ---------
        @param table:
        ---------
        @result:
        """

        # ??? SCAN ????????????????????????????????? 0 ?????? ??????????????????????????????????????? ???????????????????????????????????? 0 ??????????????? ?????????????????????
        cursor = "0"
        while cursor != 0:
            cursor, data = self._redis.sscan(table, cursor=cursor, count=500)
            for item in data:
                # pipe.srem(table, item)
                self._redis.srem(table, item)

            # pipe.execute()

    def sismember(self, table, key):
        "Return a boolean indicating if ``value`` is a member of set ``name``"
        return self._redis.sismember(table, key)

    def zadd(self, table, values, prioritys=0):
        """
        @summary: ????????????set????????????????????? ??????(???????????????)
        ---------
        @param table:
        @param values: ?????? ??????list ??? ?????????
        @param prioritys: ???????????? double???????????????list ??? ???????????? ??????????????????????????????, ????????????????????? ?????????????????????value???????????????0
        ---------
        @result:??????????????? ??????0????????????????????????1??? ?????????????????? [0, 1 ...]
        """
        if isinstance(values, list):
            if not isinstance(prioritys, list):
                prioritys = [prioritys] * len(values)
            else:
                assert len(values) == len(prioritys), "values?????????prioritys???????????????"

            pipe = self._redis.pipeline()

            if not self._is_redis_cluster:
                pipe.multi()
            for value, priority in zip(values, prioritys):
                pipe.execute_command(
                    "ZADD", table, priority, value
                )  # ????????????2.x???3.x?????????redis
            return pipe.execute()

        else:
            return self._redis.execute_command(
                "ZADD", table, prioritys, values
            )  # ????????????2.x???3.x?????????redis

    def zget(self, table, count=1, is_pop=True):
        """
        @summary: ?????????set????????????????????? ?????????????????????????????????????????????
        ---------
        @param table:
        @param count: ?????? -1 ??????????????????
        @param is_pop:??????????????????????????????set???????????????????????????
        ---------
        @result: ??????
        """

        start_pos = 0  # ??????
        end_pos = count - 1 if count > 0 else count

        pipe = self._redis.pipeline()

        if not self._is_redis_cluster:
            pipe.multi()  # ????????????????????? ?????? http://www.runoob.com/redis/redis-transactions.html
        pipe.zrange(table, start_pos, end_pos)  # ??????
        if is_pop:
            pipe.zremrangebyrank(table, start_pos, end_pos)  # ??????
        results, *count = pipe.execute()
        return results

    def zremrangebyscore(self, table, priority_min, priority_max):
        """
        ???????????????????????? ?????????
        @param table:
        @param priority_min:
        @param priority_max:
        @return: ????????????????????????
        """
        return self._redis.zremrangebyscore(table, priority_min, priority_max)

    def zrangebyscore(self, table, priority_min, priority_max, count=None, is_pop=True):
        """
        @summary: ????????????????????????????????? ?????????
        ---------
        @param table:
        @param priority_min: ????????????????????????
        @param priority_max:
        @param count: ???????????????????????????????????????????????????????????????
        @param is_pop: ????????????
        ---------
        @result:
        """

        # ??????lua????????? ????????????????????????
        lua = """
            -- local key = KEYS[1]
            local min_score = ARGV[2]
            local max_score = ARGV[3]
            local is_pop = ARGV[4]
            local count = ARGV[5]

            -- ??????
            local datas = nil
            if count then
                datas = redis.call('zrangebyscore', KEYS[1], min_score, max_score, 'limit', 0, count)
            else
                datas = redis.call('zrangebyscore', KEYS[1], min_score, max_score)
            end

            -- ??????redis??????????????????
            if (is_pop=='True' or is_pop=='1') then
                for i=1, #datas do
                    redis.call('zrem', KEYS[1], datas[i])
                end
            end


            return datas

        """
        cmd = self._redis.register_script(lua)
        if count:
            res = cmd(
                keys=[table], args=[table, priority_min, priority_max, is_pop, count]
            )
        else:
            res = cmd(keys=[table], args=[table, priority_min, priority_max, is_pop])

        return res

    def zrangebyscore_increase_score(
            self, table, priority_min, priority_max, increase_score, count=None
    ):
        """
        @summary: ????????????????????????????????? ???????????? ??????????????????
        ---------
        @param table:
        @param priority_min: ????????????
        @param priority_max: ????????????
        @param increase_score: ??????????????? ??????????????????????????????????????????????????????
        @param count: ???????????????????????????????????????????????????????????????
        ---------
        @result:
        """

        # ??????lua????????? ????????????????????????
        lua = """
            -- local key = KEYS[1]
            local min_score = ARGV[1]
            local max_score = ARGV[2]
            local increase_score = ARGV[3]
            local count = ARGV[4]

            -- ??????
            local datas = nil
            if count then
                datas = redis.call('zrangebyscore', KEYS[1], min_score, max_score, 'limit', 0, count)
            else
                datas = redis.call('zrangebyscore', KEYS[1], min_score, max_score)
            end

            --???????????????
            for i=1, #datas do
                redis.call('zincrby', KEYS[1], increase_score, datas[i])
            end

            return datas

        """
        cmd = self._redis.register_script(lua)
        if count:
            res = cmd(
                keys=[table], args=[priority_min, priority_max, increase_score, count]
            )
        else:
            res = cmd(keys=[table], args=[priority_min, priority_max, increase_score])

        return res

    def zrangebyscore_set_score(
            self, table, priority_min, priority_max, score, count=None
    ):
        """
        @summary: ????????????????????????????????? ???????????? ??????????????????
        ---------
        @param table:
        @param priority_min: ????????????
        @param priority_max: ????????????
        @param score: ?????????
        @param count: ???????????????????????????????????????????????????????????????
        ---------
        @result:
        """

        # ??????lua????????? ????????????????????????
        lua = """
            -- local key = KEYS[1]
            local min_score = ARGV[1]
            local max_score = ARGV[2]
            local set_score = ARGV[3]
            local count = ARGV[4]

            -- ??????
            local datas = nil
            if count then
                datas = redis.call('zrangebyscore', KEYS[1], min_score, max_score, 'withscores','limit', 0, count)
            else
                datas = redis.call('zrangebyscore', KEYS[1], min_score, max_score, 'withscores')
            end

            local real_datas = {} -- ??????
            --???????????????
            for i=1, #datas, 2 do
               local data = datas[i]
               local score = datas[i+1]

               table.insert(real_datas, data) -- ????????????

               redis.call('zincrby', KEYS[1], set_score - score, datas[i])
            end

            return real_datas

        """
        cmd = self._redis.register_script(lua)
        if count:
            res = cmd(keys=[table], args=[priority_min, priority_max, score, count])
        else:
            res = cmd(keys=[table], args=[priority_min, priority_max, score])

        return res

    def zincrby(self, table, amount, value):
        return self._redis.zincrby(table, amount, value)

    def zget_count(self, table, priority_min=None, priority_max=None):
        """
        @summary: ????????????????????????
        ---------
        @param table:
        @param priority_min:??????????????? ?????????????????????
        @param priority_max:??????????????? ?????????????????????
        ---------
        @result:
        """

        if priority_min != None and priority_max != None:
            return self._redis.zcount(table, priority_min, priority_max)
        else:
            return self._redis.zcard(table)

    def zrem(self, table, values):
        """
        @summary: ??????????????????????????????
        ---------
        @param table:
        @param values: ??????????????????
        ---------
        @result:
        """

        if isinstance(values, list):
            self._redis.zrem(table, *values)
        else:
            self._redis.zrem(table, values)

    def zexists(self, table, values):
        """
        ??????zscore???????????????????????????
        @param values:
        @return:
        """

        is_exists = []

        if isinstance(values, list):
            pipe = self._redis.pipeline()
            pipe.multi()
            for value in values:
                pipe.zscore(table, value)
            is_exists_temp = pipe.execute()
            for is_exist in is_exists_temp:
                if is_exist != None:
                    is_exists.append(1)
                else:
                    is_exists.append(0)

        else:
            is_exists = self._redis.zscore(table, values)
            is_exists = 1 if is_exists != None else 0

        return is_exists

    def lpush(self, table, values):

        if isinstance(values, list):
            pipe = self._redis.pipeline()

            if not self._is_redis_cluster:
                pipe.multi()
            for value in values:
                pipe.rpush(table, value)
            pipe.execute()

        else:
            return self._redis.rpush(table, values)

    def lpop(self, table, count=1):
        """
        @summary:
        ---------
        @param table:
        @param count:
        ---------
        @result: count>1???????????????
        """

        datas = None

        count = count if count <= self.lget_count(table) else self.lget_count(table)

        if count:
            if count > 1:
                pipe = self._redis.pipeline()

                if not self._is_redis_cluster:
                    pipe.multi()
                while count:
                    pipe.lpop(table)
                    count -= 1
                datas = pipe.execute()

            else:
                datas = self._redis.lpop(table)

        return datas

    def rpoplpush(self, from_table, to_table=None):
        """
        ????????? from_table ????????????????????????(?????????)?????????????????????????????????
        ??? from_table ?????????????????????????????? to_table ????????? to_table ????????????????????????
        ?????? from_table ??? to_table ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????(rotation)??????
        @param from_table:
        @param to_table:
        @return:
        """

        if not to_table:
            to_table = from_table

        return self._redis.rpoplpush(from_table, to_table)

    def lget_count(self, table):
        return self._redis.llen(table)

    def lrem(self, table, value, num=0):
        """
        @summary:
        ??????value
        ---------
        @param table:
        @param value:
        @param num:
        ---------
        @result: ???????????????
        """
        return self._redis.lrem(table, num, value)

    def lrange(self, table, start=0, end=-1):
        return self._redis.lrange(table, start, end)

    def hset(self, table, key, value):
        """
        @summary:
        ?????? key ??????????????????????????????????????????????????? HSET ?????????
        ????????? field ????????????????????????????????????????????????
        ---------
        @param table:
        @param key:
        @param value:
        ---------
        @result: 1 ???????????? 0 ??????
        """
        return self._redis.hset(table, key, value)

    def hset_batch(self, table, datas):
        """
        ????????????
        Args:
            datas:
                [[key, value]]
        Returns:

        """
        pipe = self._redis.pipeline()

        if not self._is_redis_cluster:
            pipe.multi()
        for key, value in datas:
            pipe.hset(table, key, value)
        return pipe.execute()

    def hincrby(self, table, key, increment):
        return self._redis.hincrby(table, key, increment)

    def hget(self, table, key, is_pop=False):
        if not is_pop:
            return self._redis.hget(table, key)
        else:
            lua = """
                -- local key = KEYS[1]
                local field = ARGV[1]

                -- ??????
                local datas = redis.call('hget', KEYS[1], field)
                -- ?????????
                redis.call('hdel', KEYS[1], field)

                return datas

                    """
            cmd = self._redis.register_script(lua)
            res = cmd(keys=[table], args=[key])

            return res

    def hgetall(self, table):
        return self._redis.hgetall(table)

    def hexists(self, table, key):
        return self._redis.hexists(table, key)

    def hdel(self, table, *keys):
        """
        @summary: ???????????????key ????????????
        ---------
        @param table:
        @param *keys:
        ---------
        @result:
        """
        self._redis.hdel(table, *keys)

    def hget_count(self, table):
        return self._redis.hlen(table)

    def hkeys(self, table):
        return self._redis.hkeys(table)

    def setbit(self, table, offsets, values):
        """
        ??????????????????????????????????????? ??????????????????
        @param table:
        @param offsets: ????????????????????????
        @param values: ????????????????????????
        @return: list / ?????????
        """
        if isinstance(offsets, list):
            if not isinstance(values, list):
                values = [values] * len(offsets)
            else:
                assert len(offsets) == len(values), "offsets?????????values???????????????"

            pipe = self._redis.pipeline()
            pipe.multi()

            for offset, value in zip(offsets, values):
                pipe.setbit(table, offset, value)

            return pipe.execute()

        else:
            return self._redis.setbit(table, offsets, values)

    def getbit(self, table, offsets):
        """
        ?????????????????????????????????
        @param table:
        @param offsets: ????????????
        @return: list / ?????????
        """
        if isinstance(offsets, list):
            pipe = self._redis.pipeline()
            pipe.multi()
            for offset in offsets:
                pipe.getbit(table, offset)

            return pipe.execute()

        else:
            return self._redis.getbit(table, offsets)

    def bitcount(self, table):
        return self._redis.bitcount(table)

    def strset(self, table, value, **kwargs):
        return self._redis.set(table, value, **kwargs)

    def str_incrby(self, table, value):
        return self._redis.incrby(table, value)

    def strget(self, table):
        return self._redis.get(table)

    def strlen(self, table):
        return self._redis.strlen(table)

    def getkeys(self, regex):
        return self._redis.keys(regex)

    def exists_key(self, key):
        return self._redis.exists(key)

    def set_expire(self, key, seconds):
        """
        @summary: ??????????????????
        ---------
        @param key:
        @param seconds: ???
        ---------
        @result:
        """
        self._redis.expire(key, seconds)

    def get_expire(self, key):
        """
        @summary: ??????????????????
        ---------
        @param key:
        @param seconds: ???
        ---------
        @result:
        """
        return self._redis.ttl(key)

    def clear(self, table):
        try:
            self._redis.delete(table)
        except Exception as e:
            logger.error(e)

    def get_redis_obj(self):
        return self._redis

    def _reconnect(self):
        # ??????????????????, ??????????????????????????? timeout ?????????????????????????????????
        retry_count = 0
        while True:
            try:
                retry_count += 1
                logger.error(f"redis ????????????, ???????????? {retry_count}")
                if self.get_connect():
                    logger.info(f"redis ????????????")
                    return True
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"???????????? e: {e}")

            time.sleep(2)

    def __getattr__(self, name):
        return getattr(self._redis, name)

    def current_status(self, show_key=True, filter_key_by_used_memory=10 * 1024 * 1024):
        """
        ??????redis??????????????????
        Args:
            show_key: ??????????????????key?????????
            filter_key_by_used_memory: ??????????????????????????????key ???????????????????????????????????????key

        Returns:

        """
        from prettytable import PrettyTable
        from tqdm import tqdm

        status_msg = ""

        print("???????????????????????????...")
        clients_count = self._redis.execute_command("info clients")
        max_clients_count = self._redis.execute_command("config get maxclients")
        status_msg += ": ".join(max_clients_count) + "\n"
        status_msg += clients_count + "\n"

        print("????????????????????????????????????...")
        total_status = self._redis.execute_command("info memory")
        status_msg += total_status + "\n"

        if show_key:
            print("??????????????????key???????????????????????????...")
            table = PrettyTable(
                field_names=[
                    "type",
                    "key",
                    "value_count",
                    "used_memory_human",
                    "used_memory",
                ],
                sortby="used_memory",
                reversesort=True,
                header_style="title",
            )

            keys = self._redis.execute_command("keys *")
            for key in tqdm(keys):
                key_type = self._redis.execute_command("type {}".format(key))
                if key_type == "set":
                    value_count = self._redis.scard(key)
                elif key_type == "zset":
                    value_count = self._redis.zcard(key)
                elif key_type == "list":
                    value_count = self._redis.llen(key)
                elif key_type == "hash":
                    value_count = self._redis.hlen(key)
                elif key_type == "string":
                    value_count = self._redis.strlen(key)
                elif key_type == "none":
                    continue
                else:
                    raise TypeError("???????????? {} ?????????key".format(key_type))

                used_memory = self._redis.execute_command("memory usage {}".format(key))
                if used_memory >= filter_key_by_used_memory:
                    used_memory_human = (
                        "%0.2fMB" % (used_memory / 1024 / 1024) if used_memory else 0
                    )

                    table.add_row(
                        [key_type, key, value_count, used_memory_human, used_memory]
                    )

            status_msg += str(table)

        return status_msg
