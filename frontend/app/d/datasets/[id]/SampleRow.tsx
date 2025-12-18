"use client"

import { Samples } from "@/lib/schema";

function SampleRow({ sample, id }: { sample: Samples, id: string }) {
    return (
        <tr className="w-full h-8 hover:cursor-pointer hover:bg-gray-100" key={String(sample.id)}
            onClick={() => window.location.href = `/d/datasets/${id}/${sample.id}`}
        >
            <td>{sample.sample_text}</td>
        </tr>
    );
}

export default SampleRow;