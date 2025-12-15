import { findFeatures } from "@/lib/actions/features";
import FeatureCard from "./FeatureCard";

async function FeaturesPage() {
    const features = await findFeatures({})

    return (
        <div>
            {features.map((feature) =>
                //@ts-expect-error description: created_at type mismatch
                <FeatureCard {...feature} />)}
        </div>

    );
}

export default FeaturesPage;