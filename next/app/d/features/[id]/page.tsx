import { db } from "@/lib/db";
import { sql } from "kysely";
import ExplanationCard from "./ExplanationCard";
import ActivationCard from "./ActivationCard";
import { Activations } from "@/lib/schema";

async function FeaturePage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params
    const explanations = await sql`select * from explanations where feature_id=${id}`.execute(db)

    const activations = await sql<Activations & { tokens: string[] }>`
    select a.*, s.tokens 
from activations a 
left join samples s 
on s.id = a.sample_id
where a.feature_id=${id}
`.execute(db)
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
                <h2>Activations</h2>
                <div>
                    {
                        //@ts-expect-error description: key error
                        activations.rows.map((activation) => <ActivationCard {...activation} key={activation.id} />)
                    }
                </div>
            </div>
        </div>
    );
}

export default FeaturePage;