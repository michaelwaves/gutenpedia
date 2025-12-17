import { Activations } from "@/lib/schema";

function ActivationCard({ values, tokens }: Partial<Activations> & { tokens: [] }) {
    return (
        <div className="flex flex-col gap-4 p-4 w-full max-w-2xl h-40 rounded-md outline ">

            <div className="flex flex-row">
                {
                    tokens.map((token, i) => <TokenDisplay token={token} value={values[i]} key={i} />)
                }
            </div>

        </div>
    );
}

export default ActivationCard;


type TokenDisplayProps = {
    token: string
    value: string
}

function TokenDisplay({ token, value }: TokenDisplayProps) {
    const intensity = Math.max(0, Math.min(1, Number(value) / 100)); // 0 → 1

    return (
        <span
            className="px-1 rounded"
            style={{
                backgroundColor: `rgb(${255 - intensity * 155}, 255, ${255 - intensity * 155})`
            }}
        >
            {token}
        </span>
    )
}