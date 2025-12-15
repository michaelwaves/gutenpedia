import { findDatasets } from "@/lib/actions/datasets";
import DatasetCard from "./DatasetCard";

async function DatasetPage() {
    const datasets = await findDatasets({})
    return (
        <div>
            <div>
                <h1 className="text-xl">Datasets</h1>
            </div>
            <div>

                {
                    //@ts-expect-error description: created_at date incompatibility
                    datasets.map((dataset) => <DatasetCard {...dataset} key={dataset.id} />)}
            </div>
        </div>
    );
}

export default DatasetPage;

