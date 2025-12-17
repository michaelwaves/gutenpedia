import NextAuth, { type DefaultSession } from 'next-auth'
import Google from "next-auth/providers/google"
import Github from "next-auth/providers/github"
import PostgresAdapter from '@auth/pg-adapter'
import { Pool } from "pg"

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
})

declare module "next-auth" {
    interface Session {
        user: {
            handle: string
        } & DefaultSession["user"]
    }
}

declare module "@auth/pg-adapter" {
    interface AdapterUser {
        handle?: string
    }
}

export const { handlers, signIn, signOut, auth } = NextAuth({
    adapter: PostgresAdapter(pool),
    providers: [Google, Github],
    callbacks: {
        session({ session, user }) {
            session.user.id = user.id
            //@ts-expect-error description: i added handle to users in database
            session.user.handle = user.handle;
            return session
        },
    }
})