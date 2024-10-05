import React, { useState } from "react";

const SwipeComponent = () => {
    const [swipeStatus, setSwipeStatus] = useState(null);

    async function signAndSubmitSwipe(user_id, accelerator_id, swipe_direction) {
        try {
            const response = await fetch("/swipe", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_id: user_id,
                    accelerator_id: accelerator_id,
                    swipe_direction: swipe_direction,
                }),
            });

            const data = await response.json();
            setSwipeStatus("Swipe stored: " + JSON.stringify(data));
        } catch (error) {
            console.error("Error storing swipe:", error);
            setSwipeStatus("Error storing swipe: " + error.message);
        }
    }

    // Sample user and accelerator data
    const userId = "sampleUser123";
    const acceleratorId = "accelerator123";

    return (
        <div>
            <h2>Swipe for Accelerators</h2>
            <button onClick={() => signAndSubmitSwipe(userId, acceleratorId, "right")}>
                Swipe Right
            </button>
            <button onClick={() => signAndSubmitSwipe(userId, acceleratorId, "left")}>
                Swipe Left
            </button>
            {swipeStatus && <p>{swipeStatus}</p>}
        </div>
    );
};

export default SwipeComponent;
