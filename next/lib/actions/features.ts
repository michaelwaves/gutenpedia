import { Insertable, Updateable } from "kysely";
import { db } from "../db";
import { Features } from "../schema";


export async function findFeatureById(id: string) {
    return await db.selectFrom('features').where('id', '=', id)
        .selectAll()
        .executeTakeFirstOrThrow()
}

export async function findFeatures(criteria: Partial<Features>) {
    let query = db.selectFrom('features')
    if (criteria.feature_index) {
        query = query.where('feature_index', '=', criteria.feature_index)
    }
    if (criteria.created_by) {
        query = query.where('created_by', '=', criteria.created_by)
    }
    if (criteria.model_id) {
        query = query.where('model_id', '=', criteria.model_id)
    }
    if (criteria.layer) {
        query = query.where('layer', '=', criteria.layer)
    }
    return await query.selectAll().execute()
}

export async function updateFeature(id: string, updateWith: Updateable<Features>) {
    await db.updateTable('features').set(updateWith).where('id', '=', id).execute()
}


export async function createFeature(dataset: Insertable<Features>) {
    return await db.insertInto('features')
        .values(dataset)
        .returningAll()
        .executeTakeFirstOrThrow()
}

export async function deleteFeature(id: string) {
    return await db.deleteFrom('features').where('id',
        '=', id
    )
        .returningAll()
        .executeTakeFirst()
}