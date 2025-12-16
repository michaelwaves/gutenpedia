import { findFeatures } from "@/lib/actions/features";
import FeatureCard from "./FeatureCard";
import { sql } from "kysely";
import { db } from "@/lib/db";
import { Features } from "@/lib/schema";

async function FeaturesPage() {
    const features = await sql`select f.*, e.description as explanation from features f
    INNER JOIN(
    SELECT DISTINCT ON (feature_id) *
    FROM explanations
    ORDER BY feature_id, created_at DESC
    ) e ON e.feature_id = f.id
    limit 50`.execute(db)

    return (
        <div className="flex flex-col gap-2">
            {features.rows.map((feature) =>
                //@ts-expect-error description: created_at type mismatch
                <FeatureCard {...feature} key={feature.id} />)}
        </div>

    );
}

export default FeaturesPage;