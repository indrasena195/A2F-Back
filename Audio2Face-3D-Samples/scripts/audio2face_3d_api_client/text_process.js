const text = document.getElementById("textToConvert");
const convertBtn = document.getElementById("convertBtn");
const error = document.querySelector('.error-para');

convertBtn.addEventListener('click', async function () {
    const enteredText = text.value.trim();

    if (!enteredText.length) {
        error.textContent = "Nothing to Convert! Enter text in the text area.";
        return;
    }

    error.textContent = "";

    try {
        await fetch('http://localhost:2000/send-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: enteredText }),
        });
        console.log("Text sent successfully to the backend.");

        if (!response.ok) {
            throw new Error('Error processing text');
        }

        text.value = ""; 

        // const data = await response.text();
        // console.log("Processed data:", data);
    } catch (error) {
        console.error("Error fetching data:", error);
        error.textContent = "An error occurred while processing your request.";
    }
});
