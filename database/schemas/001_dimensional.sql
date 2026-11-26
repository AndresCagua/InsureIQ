-- Initial dimensional warehouse contract for PostgreSQL.
create schema if not exists raw;
create schema if not exists staging;
create schema if not exists silver;
create schema if not exists gold;
create schema if not exists audit;

create table if not exists gold.dim_customer (
    customer_key bigint generated always as identity primary key,
    customer_id text not null unique,
    age integer not null check (age between 18 and 100),
    province text not null,
    is_synthetic boolean not null
);

create table if not exists gold.dim_vehicle (
    vehicle_key bigint generated always as identity primary key,
    vehicle_id text not null unique,
    make text not null,
    model_year integer not null,
    vehicle_value_usd numeric(18, 2) not null check (vehicle_value_usd > 0),
    is_synthetic boolean not null
);

create table if not exists gold.dim_policy (
    policy_key bigint generated always as identity primary key,
    policy_id text not null unique,
    customer_id text not null references gold.dim_customer(customer_id),
    vehicle_id text not null references gold.dim_vehicle(vehicle_id),
    product text not null,
    annual_premium_usd numeric(18, 2) not null check (annual_premium_usd > 0),
    is_synthetic boolean not null
);

create table if not exists gold.fact_claim (
    claim_key bigint generated always as identity primary key,
    claim_id text not null unique,
    policy_id text not null references gold.dim_policy(policy_id),
    loss_date date not null,
    claimed_amount_usd numeric(18, 2) not null check (claimed_amount_usd >= 0),
    is_synthetic boolean not null
);
