import { db } from "@/lib/db";
import { sql } from "kysely";
import SampleRow from "./SampleRow";

async function DatasetPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params
    const samples = await sql`select * from samples where dataset_id=${id}`.execute(db)
    return (
        <div>
            <table>
                <thead>
                    <tr>
                        <th>Text</th>
                    </tr>
                </thead>
                <tbody>
                    {samples.rows.map((sample) => <SampleRow id={id} sample={sample} />)}
                </tbody>
            </table>
        </div>
    );
}

export default DatasetPage;