import { Insertable, Updateable } from "kysely";
import { db } from "../db";
import { Users } from "../schema";


export async function findUserById(id: number) {
    return await db.selectFrom('users').where('id', '=', id)
        .selectAll()
        .executeTakeFirstOrThrow()
}

export async function findUsers(criteria: Partial<Users>) {
    let query = db.selectFrom('users')
    if (criteria.email) {
        query = query.where('email', '=', criteria.email)
    }
    if (criteria.name) {
        query = query.where('name', '=', criteria.name)
    }
    return await query.selectAll().execute()
}

export async function updateUser(id: number, updateWith: Updateable<Users>) {
    await db.updateTable('users').set(updateWith).where('id', '=', id).execute()
}


export async function createUser(user: Insertable<Users>) {
    return await db.insertInto('users')
        .values(user)
        .returningAll()
        .executeTakeFirstOrThrow()
}

export async function deletePerson(id: number) {
    return await db.deleteFrom('users').where('id',
        '=', id
    )
        .returningAll()
        .executeTakeFirst()
}