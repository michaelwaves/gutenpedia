import { db } from "@/lib/db";
import { sql } from "kysely";
import ExplanationCard from "./ExplanationCard";

async function FeaturePage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params
    const explanations = await sql`select * from explanations where feature_id=${id}`.execute(db)
    return (
        <div>
            <h1>Feature {id}</h1>
            <div>
                <h2>Explanations</h2>
                <div>
                    {
                        //@ts-expect-error description:  explanation bug
                        explanations.rows.map((explanation) => <ExplanationCard {...explanation} key={explanation.id} />)}
                </div>
            </div>
        </div>
    );
}

export default FeaturePage;