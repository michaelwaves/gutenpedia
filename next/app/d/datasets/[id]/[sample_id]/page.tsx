import { sql } from "kysely";

async function SampleFeaturesPage({ params }: { params: Promise<{ id: string, sample_id: string }> }) {
    const { sample_id } = await params
    const activations = await sql`select * from activations where sample_id=${sample_id}`
    return (
        <div>
        </div>
    );
}

export default SampleFeaturesPage;