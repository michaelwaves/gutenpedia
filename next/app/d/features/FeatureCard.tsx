"use client"
import { Features } from "@/lib/schema";
import { Copy } from "lucide-react";

function FeatureCard({ feature_index, model_id, layer, id, explanation }: Partial<Features> & { explanation: string }) {

    return (
        <div onClick={() => window.location.href = `/d/features/${id}`} className="flex flex-col gap-4 p-4 w-full max-w-2xl h-40 rounded-md outline hover:bg-gray-100 animate transition-colors">
            <h1 className="text-xl flex flex-row gap-2 items-center">{String(explanation)} <Copy onClick={(e) => {
                e.stopPropagation(); window.navigator.clipboard.writeText(String(id))
            }} className="hover:cursor-pointer w-4 h-4 text-gray-600" /></h1>

            <p className="font-semibold text-gray-600 text-sm flex flex-row gap-2 items-center"><span>{String(id)}</span> <Copy onClick={(e) => {
                e.stopPropagation(); window.navigator.clipboard.writeText(String(id))
            }} className="hover:cursor-pointer w-4 h-4" /></p>
            <div className="flex flex-row gap-2 text-sm">
                <p><span className="font-semibold">Index: </span>{feature_index}</p>
                <p><span className="font-semibold">Layer: </span>{layer}</p>
                <p><span className="font-semibold">Model: </span>{model_id}</p>
            </div>

        </div>
    );
}

export default FeatureCard;