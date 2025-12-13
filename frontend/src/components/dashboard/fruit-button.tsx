import { Button } from "../ui/button";

function FruitButton() {
    const getFruits = async () => {
        const res = await fetch("http://localhost:8001/api")
        console.log(res)
        console.log(await res.json())

    }
    return (
        <Button variant={"default"} className="bg-gray-800 hover:cursor-pointer hover:bg-gray-700 animate-color " onClick={getFruits}>🍎🍐🍍</Button>
    );
}

export default FruitButton;