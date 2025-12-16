import { sql } from "kysely";

async function FeaturePage(params: Promise<{ id: string }>) {
    const { id } = await params
    const features = sql`select * from features where id=${id}`
    return (
        <div>
            Feature {id}
        </div>
    );
}

export default FeaturePage;