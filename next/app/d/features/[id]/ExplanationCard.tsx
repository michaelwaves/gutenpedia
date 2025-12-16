"use client"
import { Explanations } from "@/lib/schema";
import { Copy } from "lucide-react";

function ExplanationCard({ feature_index, model_id, layer, id, description }: Partial<Explanations>) {

    return (
        <div className="flex flex-col gap-4 p-4 w-full max-w-2xl h-40 rounded-md outline hover:bg-gray-100 animate transition-colors">
            <h1 className="text-xl flex flex-row gap-2 items-center">{String(description)} <Copy onClick={() => window.navigator.clipboard.writeText(String(id))} className="hover:cursor-pointer w-4 h-4 text-gray-600" /></h1>

            <p className="font-semibold text-gray-600 text-sm flex flex-row gap-2 items-center"><span>{String(id)}</span> <Copy onClick={() => window.navigator.clipboard.writeText(String(id))} className="hover:cursor-pointer w-4 h-4" /></p>
        </div>
    );
}

export default ExplanationCard;