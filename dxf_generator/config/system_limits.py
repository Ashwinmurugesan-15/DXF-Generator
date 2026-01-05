from dxf_generator.config.env_config import config

# System-level limits for the DXF Generator

MAX_BATCH_SIZE = config.MAX_BATCH_SIZE           # Maximum number of items in a single batch request
MAX_TOTAL_REQUESTS_PER_MIN = 100 # (Reserved for future rate limiting)
MAX_FILE_SIZE_MB = 10         # Maximum size of a single generated file (not strictly enforced yet)
