import { Features } from "@/lib/schema";

function FeatureCard({ feature_index, model_id, }: Partial<Features>) {
    return (
        <div>
            {feature_index}
        </div>
    );
}

export default FeatureCard;