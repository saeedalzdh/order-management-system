from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "addresses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "city" VARCHAR(100) NOT NULL,
    "street" VARCHAR(255) NOT NULL,
    "postal_code" VARCHAR(20) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "customers" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "phone" VARCHAR(20) NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "orders" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "channel_order_id" VARCHAR(255) NOT NULL,
    "account_id" VARCHAR(255) NOT NULL,
    "brand_id" VARCHAR(255) NOT NULL,
    "pickup_time" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "address_id" INT NOT NULL REFERENCES "addresses" ("id") ON DELETE CASCADE,
    "customer_id" INT NOT NULL REFERENCES "customers" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "order_items" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "plu" VARCHAR(50) NOT NULL,
    "quantity" INT NOT NULL,
    "order_id" INT NOT NULL REFERENCES "orders" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "order_status_history" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" INT NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "duration" INT,
    "order_id" INT NOT NULL REFERENCES "orders" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_order_statu_order_i_7965a8" ON "order_status_history" ("order_id", "timestamp");
CREATE TABLE IF NOT EXISTS "analytics_customer_lifetime_metrics" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "customer_id" INT NOT NULL UNIQUE,
    "order_count" INT NOT NULL,
    "first_order_at" TIMESTAMPTZ NOT NULL,
    "last_order_at" TIMESTAMPTZ NOT NULL,
    "avg_order_frequency_days" DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS "idx_analytics_c_custome_403df5" ON "analytics_customer_lifetime_metrics" ("customer_id");
CREATE INDEX IF NOT EXISTS "idx_analytics_c_order_c_4b28fc" ON "analytics_customer_lifetime_metrics" ("order_count");
CREATE TABLE IF NOT EXISTS "analytics_hourly_order_metrics" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "date" DATE NOT NULL,
    "hour" INT NOT NULL,
    "throughput" INT NOT NULL,
    CONSTRAINT "uid_analytics_h_date_b3f91d" UNIQUE ("date", "hour")
);
CREATE INDEX IF NOT EXISTS "idx_analytics_h_date_30fd88" ON "analytics_hourly_order_metrics" ("date");
CREATE TABLE IF NOT EXISTS "analytics_hourly_status_metrics" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "date" DATE NOT NULL,
    "hour" INT NOT NULL,
    "status" INT NOT NULL,
    "count" INT NOT NULL,
    "total_duration" INT NOT NULL,
    "avg_duration" DOUBLE PRECISION NOT NULL,
    CONSTRAINT "uid_analytics_h_date_e2fd86" UNIQUE ("date", "hour", "status")
);
CREATE INDEX IF NOT EXISTS "idx_analytics_h_date_a809e1" ON "analytics_hourly_status_metrics" ("date");
CREATE INDEX IF NOT EXISTS "idx_analytics_h_status_1eaf72" ON "analytics_hourly_status_metrics" ("status");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
