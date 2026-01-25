import builtins
import time
from typing import Final
from uuid import UUID, SafeUUID
import random
import datetime


class UUIDv7(UUID):
    last_timestamp: builtins.int = 0
    sequence: builtins.int = 0

    def __init__(
        self,
        from_int: builtins.int = 0,
        random_A: tuple[bool, builtins.int] = (True, 0),
        hex: builtins.str = "",
    ) -> None:
        """Sinh UUIDv7 với cấu trúc chi tiết
        - random_A: (bool, int) - Nếu bool là True, sinh random 12 bit A, nếu False dùng int làm A
        - from_int: int - Nếu khác 0, tạo UUIDv7 từ int này
        - hex: str - Nếu khác rỗng, tạo UUIDv7 từ chuỗi hex này
        Nếu cả from_int và hex đều không được cung cấp, sẽ sinh UUIDv7 mới hoàn toàn ngẫu nhiên.
        """
        if from_int != 0:
            super().__init__(
                hex=from_int.to_bytes(16, byteorder="big").hex(), is_safe=SafeUUID.safe
            )
            return
        if hex:
            super().__init__(hex=hex, is_safe=SafeUUID.safe)
            return
        # 1. Lấy timestamp 48 bit
        timestamp_ms = int(time.time() * 1000)

        # Xử lý trường hợp timestamp trùng
        if timestamp_ms == UUIDv7.last_timestamp:
            UUIDv7.sequence += 1
        else:
            UUIDv7.sequence = 0
            UUIDv7.last_timestamp = timestamp_ms

        # Đảm bảo timestamp 48 bit
        timestamp_48 = timestamp_ms & 0xFFFFFFFFFFFF

        if random_A[0]:
            # 2. Random A (12 bit) - có thể kết hợp với sequence
            rand_a = (random.getrandbits(12) + UUIDv7.sequence) & 0xFFF
        else:
            rand_a = random_A[1] & 0xFFF

        # 3. Version (4 bit) - luôn là 7
        version = 7

        # 4. Random B phần 1 (12 bit)
        rand_b1 = random.getrandbits(12)

        # 5. Variant (2 bit) - luôn là 10
        variant = 0b10

        # 6. Random B phần 2 (62 bit)
        rand_b2 = random.getrandbits(62)

        # Ghép các thành phần
        # Byte 0-5: timestamp (48 bit)
        uuid_int = timestamp_48 << 80

        # Byte 6-7: rand_a (12 bit) + version (4 bit)
        uuid_int |= rand_a << 68
        uuid_int |= version << 64

        # Byte 8-9: rand_b1 (12 bit) + variant (2 bit) + bắt đầu rand_b2
        uuid_int |= rand_b1 << 54
        uuid_int |= variant << 62
        uuid_int |= rand_b2 & 0x3FFFFFFFFFFFFFFF

        # Chuyển thành định dạng UUID chuẩn
        uuid_bytes = uuid_int.to_bytes(16, byteorder="big")
        uuid_hex = uuid_bytes.hex()
        super().__init__(hex=uuid_hex, is_safe=SafeUUID.safe)

    # @property.getter
    # def int(self) -> builtins.int:
    #     """Lấy giá trị int của UUIDv7"""
    #     return self.__int_
    @property
    def time(self) -> builtins.int:
        """Lấy timestamp (ms) từ UUIDv7"""
        timestamp_48 = (self.int >> 80) & 0xFFFFFFFFFFFF # type: ignore
        return timestamp_48

    @property
    def datetime(self):
        """Lấy datetime từ UUIDv7"""
        timestamp_ms = self.time
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_ms / 1000))

    @property
    def version(self) -> builtins.int:
        """Lấy version từ UUIDv7"""
        return (self.int >> 64) & 0xF # type: ignore

    @property
    def variant(self) -> str:
        """Lấy variant từ UUIDv7"""
        variant_bits = (self.int >> 62) & 0x3 # type: ignore
        if (variant_bits & 0b10) == 0b10:
            return "RFC 9562"
        elif (variant_bits & 0b110) == 0b100:
            return "Microsoft"
        elif (variant_bits & 0b1110) == 0b0000:
            return "NCS"
        else:
            return "Reserved"

    @staticmethod
    def from_int(uuid_int: builtins.int) -> "UUIDv7":
        """Tạo UUIDv7 từ int"""
        return UUIDv7(uuid_int)


class SnowflakeID(int):
    EPOCH: Final[int] = int(datetime.datetime.now().timestamp() * 1000)  # Custom epoch (ms)
    __NODE_ID_BITS: Final[int] = 10
    __SEQUENCE_BITS: Final[int] = 12
    max_node_id: Final[int] = (1 << __NODE_ID_BITS) - 1
    max_sequence: Final[int] = (1 << __SEQUENCE_BITS) - 1
    __last_timestamp: builtins.int = -1
    __sequence: builtins.int = 0
    node_id: builtins.int = -1

    @staticmethod
    def init(node_id: builtins.int) -> None:
        """Khởi tạo SnowflakeID với node_id"""
        if node_id < 0 or node_id > SnowflakeID.max_node_id:
            raise ValueError(
                f"node_id phải trong khoảng 0 đến {SnowflakeID.max_node_id}"
            )
        SnowflakeID.node_id = node_id

    @staticmethod
    def from_int(snowflake_id: builtins.int) -> "SnowflakeID":
        """Tạo SnowflakeID từ int"""
        obj = SnowflakeID.__new__(SnowflakeID)
        obj = int.__new__(SnowflakeID, snowflake_id)
        return obj

    def __new__(cls) -> "SnowflakeID":
        """Sinh Snowflake ID"""
        if SnowflakeID.node_id == -1:
            raise ValueError(
                "SnowflakeID chưa được khởi tạo. Vui lòng gọi SnowflakeID.init(node_id) trước."
            )
        timestamp = int(time.time() * 1000) - SnowflakeID.EPOCH
        if timestamp == SnowflakeID.__last_timestamp:
            SnowflakeID.__sequence = (
                SnowflakeID.__sequence + 1
            ) & SnowflakeID.max_sequence
            if SnowflakeID.__sequence == 0:
                while timestamp <= SnowflakeID.__last_timestamp:
                    timestamp = int(time.time() * 1000) - SnowflakeID.EPOCH
        else:
            SnowflakeID.__sequence = 0
        SnowflakeID.__last_timestamp = timestamp
        snowflake_id = (
            (timestamp << (SnowflakeID.__NODE_ID_BITS + SnowflakeID.__SEQUENCE_BITS))
            | (SnowflakeID.node_id << SnowflakeID.__SEQUENCE_BITS)
            | SnowflakeID.__sequence
        )
        return super().__new__(cls, snowflake_id)

    @property
    def datetime(self) -> str:
        """Lấy datetime từ Snowflake ID"""
        timestamp = (SnowflakeID.__last_timestamp + SnowflakeID.EPOCH) / 1000
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

    @property
    def timestamp(self) -> int:
        """Lấy timestamp (ms) từ Snowflake ID"""
        return SnowflakeID.__last_timestamp + SnowflakeID.EPOCH

    @property
    def node(self) -> int:
        """Lấy node_id từ Snowflake ID"""
        return SnowflakeID.node_id

    @property
    def sequence(self) -> int:
        """Lấy sequence từ Snowflake ID"""
        return self & SnowflakeID.max_sequence

    @property
    def uuid7(self) -> UUIDv7:
        """Chuyển Snowflake ID sang UUIDv7"""
        timestamp_ms = self.timestamp
        uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
        rand_a = random.getrandbits(12)
        version = 7
        rand_b1 = random.getrandbits(12)
        variant = 0b10
        rand_b2 = random.getrandbits(62)
        uuid_int |= rand_a << 68
        uuid_int |= version << 64
        uuid_int |= rand_b1 << 54
        uuid_int |= variant << 62
        uuid_int |= rand_b2 & 0x3FFFFFFFFFFFFFFF
        # uuid_bytes = uuid_int.to_bytes(16, byteorder='big')
        # uuid_hex = uuid_bytes.hex()
        return UUIDv7.from_int(uuid_int)
