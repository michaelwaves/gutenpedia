import { auth } from "@/auth";
import { db } from "@/lib/db";
import { sql } from "kysely";
import { redirect } from "next/navigation";
import React from "react";
import SampleRow from "./SampleRow";

async function FeaturesLayout({ children, params }: { children: React.ReactNode; params: Promise<{ id: string }> }) {
    const session = await auth()
    if (!session?.user) {
        redirect("/")
    }
    const { id } = await params

    const samples = await sql`select * from samples where dataset_id=${id}`.execute(db)
    return (
        <div className="flex flex-row gap-2">
            <table className="h-fit">
                <thead>
                    <tr>
                        <th>Text</th>
                    </tr>
                </thead>
                <tbody>
                    {samples.rows.map((sample) => <SampleRow id={id} sample={sample} key={sample.id} />)}
                </tbody>
            </table>
            {children}
        </div>
    );
}

export default FeaturesLayout;