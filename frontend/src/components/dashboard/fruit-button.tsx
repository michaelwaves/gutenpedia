import { useState } from "react";
import { Button } from "../ui/button";

function FruitButton() {
    const [fruits, setFruits] = useState<Array<string>>([])
    const getFruits = async () => {
        const res = await fetch("http://localhost:8001/api")
        console.log(res)
        const data = await res.json()
        if (data) {
            setFruits(data.fruits)
        }
    }
    return (
        <div>
            <Button variant={"default"} className="bg-gray-800 hover:cursor-pointer hover:bg-gray-700 animate-color" onClick={getFruits}>🍎🍐🍍</Button>

            <div className="flex flex-row gap-4">
                {fruits.map((fruit, index) => <FruitCard fruit={fruit} index={index} />)}
            </div>
        </div>
    );
}

export default FruitButton;

function FruitCard({ fruit, index }: { fruit: string; index: number }) {
    return (
        <div className="w-40 h-18 flex items-center justify-center rounded-md border-gray-200 border-1 shadow-sm ">
            <div className="flex flex-col gap-2">
                <p className="font-bold leading-tight">Fruit #{index}</p>
                <span>{fruit}</span>
            </div>
        </div>
    )
}