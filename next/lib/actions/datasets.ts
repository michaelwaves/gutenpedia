import { Insertable, Updateable } from "kysely";
import { db } from "../db";
import { Datasets } from "../schema";


export async function findDatasetById(id: number) {
    return await db.selectFrom('Datasets').where('id', '=', id)
        .selectAll()
        .executeTakeFirstOrThrow()
}

export async function findDatasets(criteria: Partial<Datasets>) {
    let query = db.selectFrom('datasets')
    if (criteria.name) {
        query = query.where('name', '=', criteria.name)
    }
    if (criteria.created_by) {
        query = query.where('name', '=', criteria.created_by)
    }
    return await query.selectAll().execute()
}

export async function updateDataset(id: string, updateWith: Updateable<Datasets>) {
    await db.updateTable('datasets').set(updateWith).where('id', '=', id).execute()
}


export async function createDataset(dataset: Insertable<Datasets>) {
    return await db.insertInto('datasets')
        .values(dataset)
        .returningAll()
        .executeTakeFirstOrThrow()
}

export async function deletePerson(id: string) {
    return await db.deleteFrom('datasets').where('id',
        '=', id
    )
        .returningAll()
        .executeTakeFirst()
}