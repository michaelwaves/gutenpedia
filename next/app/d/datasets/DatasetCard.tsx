import { Datasets } from "@/lib/schema";
import Link from "next/link";

function DatasetCard({ name, description, type, id, link, created_at }: Partial<Datasets>) {
    return (
        <Link href={`/d/datasets/${id}`} className="w-40 h-40 rounded-sm shadow-sm ">
            <div>
                <h1 className="text-xl p-4">{name}</h1>
                <p>{link}</p>
            </div>
        </Link>
    );
}

export default DatasetCard;