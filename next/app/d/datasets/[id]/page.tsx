import { db } from "@/lib/db";
import { sql } from "kysely";

async function DatasetPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params
    const samples = await sql`select * from samples where dataset_id=${id}`.execute(db)
    return (
        <div>
            <table>
                <thead>
                    <th>Text</th>
                </thead>
                {samples.rows.map((sample) => <tr className="w-full h-8 hover:cursor-pointer hover:bg-gray-100">
                    <td>{sample.sample_text}</td>
                </tr>)}
            </table>
        </div>
    );
}

export default DatasetPage;