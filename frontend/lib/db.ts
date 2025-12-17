import { Pool } from "pg";
import { Kysely, PostgresDialect } from "kysely";
import { DB } from "./schema";

if (!process.env.DATABASE_URL) {
    throw new Error("Must set env var DATABASE_URL ")
}
const dialect = new PostgresDialect({
    pool: new Pool({
        connectionString: process.env.DATABASE_URL
    })
})


export const db = new Kysely<DB>({
    dialect
})