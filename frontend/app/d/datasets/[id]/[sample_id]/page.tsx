import ActivationCard from "@/app/d/features/[id]/ActivationCard";
import { db } from "@/lib/db";
import { sql } from "kysely";

async function SampleFeaturesPage({ params }: { params: Promise<{ id: string, sample_id: string }> }) {
    const { sample_id } = await params
    const sample_data = await sql`select * from samples where id=${sample_id} limit 1`.execute(db)

    const activations = await sql`select * from activations where sample_id=${sample_id}`.execute(db)

    return (
        <div>
            {activations.rows.map(activation =>
                <ActivationCard {...activation} key={activation.id} tokens={sample_data.rows[0].tokens} />

            )}
        </div>
    );
}

export default SampleFeaturesPage;