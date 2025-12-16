import { Features } from "@/lib/schema";

function FeatureCard({ feature_index, model_id, id }: Partial<Features>) {
    return (
        <div className="flex flex-row gap-4">
            <p>{feature_index}</p>
            <p>{String(id)}</p>
        </div>
    );
}

export default FeatureCard;