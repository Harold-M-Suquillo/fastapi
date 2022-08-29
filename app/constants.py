from psycopg2 import errors
UNIQUE_VIOLATION = errors.lookup('23505')