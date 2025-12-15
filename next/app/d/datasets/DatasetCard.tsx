import { Datasets } from "@/lib/schema";

function DatasetCard({ name, description, type, id, link, created_at }: Partial<Datasets>) {
    return (
        <div className="w-40 h-40 rounded-sm shadow-sm ">
            <div>
                <h1>{name}</h1>
                <p>{link}</p>
            </div>
        </div>
    );
}

export default DatasetCard;