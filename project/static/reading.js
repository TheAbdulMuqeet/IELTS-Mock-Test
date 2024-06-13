document.addEventListener("DOMContentLoaded", () => {
    const beginContainer = document.getElementById("begin-container");
    const mcqContainer = document.getElementById("mcq-container");
    // const quesContainer = document.getElementById("question-container");
    const blanksContainer = document.getElementById("blanks-container");
    let MCQS = {};
    let BLANKS   = {};
    let score = {"Blanks" : null, "MCQs" : null};

    document.getElementById("getBlanks").addEventListener("click", () => {
        fetch("/get-blanks", { method: "GET" })
            .then((response) => response.json())
            .then((data) => {
                blanksContainer.innerHTML = "";
                blanksContainer.style.display = "flex";

                // quesContainer.style.display = "none";
                beginContainer.style.display = "none";
                mcqContainer.style.display = "none";

                const form = document.createElement("form");
                form.setAttribute("id", "blanks-form");
                form.classList.add("submit-form");

                Object.entries(data).forEach(([correctAnswer, sentence], index) => {
                    BLANKS[index] = correctAnswer;

                    const questionDiv = document.createElement("div");

                    const heading = document.createElement("h3");
                    sentence = sentence.replace("***", `<input type='text' class='blanks' name='blank-${index}'/>`)
                    heading.innerHTML = `<strong>${index + 1}</strong>. ${sentence}`;

                    questionDiv.appendChild(heading);
                    form.appendChild(questionDiv);
                });

                // Create and append submit button to the form
                const submitButton = document.createElement("button");
                submitButton.setAttribute("type", "submit");
                submitButton.setAttribute("class", "submit-btn");
                submitButton.setAttribute("id", "b-submit");
                submitButton.textContent = "Submit";
                submitButton.disabled = true; // Initially disable the submit button
                form.appendChild(submitButton);

                // Add event listener to the form submission
                form.addEventListener("submit", (event) => {
                    event.preventDefault();
                    submitBlanks();
                });

                blanksContainer.appendChild(form);

                // Check if all inputs are filled
                const checkAllFilled = () => {
                    const allFilled = Array.from(form.querySelectorAll('input[type="text"]')).every(input => input.value.trim() !== "");
                    submitButton.disabled = !allFilled;
                };

                // Add event listeners to each input
                form.querySelectorAll('input[type="text"]').forEach((input) => {
                    input.addEventListener('input', checkAllFilled);
                });
            });
    });


    function submitBlanks() {
        const form = document.getElementById('blanks-form');
        const formData = new FormData(form);
        let correctAnswers = 0;
        
        for (const [index, correctAnswer] of Object.entries(BLANKS)) {
            const inputElement = document.querySelector(`input[name="blank-${index}"]`);
            if (inputElement) {
                const value = inputElement.value;
                inputElement.classList.remove('correct', 'incorrect');
                if (correctAnswer.toLowerCase() === value.trim().toLowerCase()) {
                    correctAnswers++;
                    inputElement.classList.add('correct');
                } else {
                    inputElement.classList.add('incorrect');
                }
            }
        };
        score["Blanks"] = correctAnswers * 2;
        console.log(score)
        showNotification(`You got <b>${correctAnswers} out of ${Object.keys(MCQS).length}</b> correct.<br><br>Your total score is ${score['MCQs'] + score['Blanks']}/40.<br><b>MCQs:</b> ${score['MCQs']}<br><b>Fill in the blanks:</b> ${score['Blanks']}`);
    }


    // Populate MCQs
    document.getElementById("getMCQs").addEventListener("click", () => {
        fetch("/get-mcqs", { method: "GET" })
            .then((response) => response.json())
            .then((data) => {
                // quesContainer.style.display = "none";
                beginContainer.style.display = "none";
                blanksContainer.style.display = "none";

                mcqContainer.innerHTML = "";
                mcqContainer.style.display = "flex";

                const form = document.createElement("form");
                form.setAttribute("id", "mcq-form");
                form.classList.add("submit-form");

                data.forEach((mcq, index) => {
                    MCQS[index] = mcq[0];
                    let heading = document.createElement("h3");
                    let qs = mcq[1].replace("***", "_______");
                    heading.innerHTML = `<strong>Q${index + 1}</strong>. ${qs}`;

                    let ul = document.createElement("ul");
                    mcq[2].forEach((option, i) => {
                        const optionElement = document.createElement("li");
                        optionElement.innerHTML = `
                            <input type="radio" id="mcq-${index}-option-${i}" name="mcq-${index}" value="${i}">
                            <label for="mcq-${index}-option-${i}">${option}</label>
                        `;
                        ul.appendChild(optionElement);
                    });

                    const question = document.createElement("div");
                    question.appendChild(heading);
                    question.appendChild(ul);

                    form.appendChild(question);
                });

                // Create and append submit button to the form
                const submitButton = document.createElement("button");
                submitButton.setAttribute("type", "submit");
                submitButton.setAttribute("class", "submit-btn");
                submitButton.setAttribute("id", "m-submit");
                submitButton.textContent = "Submit";
                submitButton.disabled = true; // Initially disable the submit button
                form.appendChild(submitButton);

                // Add event listener to the form submission
                form.addEventListener("submit", (event) => {
                    event.preventDefault();
                    submitMCQs();
                });

                mcqContainer.appendChild(form);

                // Check if all radio buttons are checked
                const checkAllChecked = () => {
                    const allChecked = Array.from(form.querySelectorAll('input[type="radio"]'))
                        .filter((input, index, array) => array
                            .filter(el => el.name === input.name)
                            .some(el => el.checked)).length / 4 === data.length;
                    submitButton.disabled = !allChecked;
                };

                // Add event listeners to each radio button
                form.querySelectorAll('input[type="radio"]').forEach((radio) => {
                    radio.addEventListener('change', checkAllChecked);
                });
            });
    });

    // Populate Questions
    // document.getElementById("getQuestions").addEventListener("click", () => {
    //     fetch("/get-questions", { method: "GET" })
    //         .then((response) => response.json())
    //         .then((data) => {
    //             // quesContainer.innerHTML = "";
    //             // quesContainer.style.display = "flex";

    //             blanksContainer.style.display = "none";
    //             beginContainer.style.display = "none";
    //             mcqContainer.style.display = "none";

    //             const form = document.createElement("form");
    //             form.setAttribute("id", "question-form");
    //             form.classList.add("submit-form");

    //             data.forEach((question, index) => {
    //                 const question_div = document.createElement("div");
    //                 let q = document.createElement("h3");
    //                 q.innerHTML = `<strong>Q${index + 1}</strong>. ${question[0]}`;
    //                 let input = document.createElement("textarea");
    //                 input.setAttribute("name", `question-${index}`);
    //                 question_div.appendChild(q);
    //                 question_div.appendChild(input);

    //                 form.appendChild(question_div);
    //             });

    //             // Create and append submit button to the form
    //             const submitButton = document.createElement("button");
    //             submitButton.setAttribute("type", "submit");
    //             submitButton.setAttribute("class", "submit-btn");
    //             submitButton.setAttribute("id", "q-submit");
    //             submitButton.textContent = "Submit";
    //             submitButton.disabled = true; // Initially disable the submit button
    //             form.appendChild(submitButton);

    //             // Add event listener to the form submission
    //             form.addEventListener("submit", (event) => {
    //                 event.preventDefault();
    //                 submitQuestions();
    //                 document.querySelectorAll('textarea').forEach((textarea) => {
    //                     textarea.value = '';
    //                 });
    //             });

    //             // quesContainer.appendChild(form);

    //             // Check if all textareas are filled
    //             const checkAllFilled = () => {
    //                 const allFilled = Array.from(form.querySelectorAll('textarea')).every(textarea => textarea.value.trim() !== "");
    //                 submitButton.disabled = allFilled ? false : true;
    //             };

    //             // Add event listeners to each textarea

    //             document.querySelectorAll('textarea').forEach((textarea) => {
    //                 textarea.addEventListener('input', checkAllFilled);
    //             });
    //         });
    // });

    function submitMCQs() {
        let correctAnswers = 0;

        for (const [index, correctOption] of Object.entries(MCQS)) {
            const selectedOption = document.querySelector(`input[name="mcq-${index}"]:checked`);
            const optionLabels = document.querySelectorAll(`input[name="mcq-${index}"] + label`);

            optionLabels.forEach((label, optionIndex) => {
                label.classList.remove('correct', 'incorrect');
                if (optionIndex === correctOption) {
                    label.classList.add('correct');
                }
                if (selectedOption && parseInt(selectedOption.value) === optionIndex) {
                    if (optionIndex === correctOption) {
                        correctAnswers++;
                    } else {
                        label.classList.add('incorrect');
                    }
                }
            });
        };

        document.querySelectorAll('#test h3').forEach((element) => { element.classList.add("submitted"); });
        score["MCQs"] = correctAnswers * 2;
        console.log(score)
        showNotification(`You got <b>${correctAnswers} out of ${Object.keys(MCQS).length}</b> correct.<br><br>Your total score is ${score['MCQs'] + score['Blanks']}/40.<br><b>MCQs:</b> ${score['MCQs']}<br><b>Fill in the blanks:</b> ${score['Blanks']}`);
    }

    // function submitQuestions() {
    //     let QUESTIONS = []
    //     const form = document.getElementById('question-form');
    //     const formData = new FormData(form);
    //     formData.forEach((value, key) => { QUESTIONS.push(value); });
    //     fetch('/submit-questions', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json'
    //         },
    //         body: JSON.stringify({ questions: QUESTIONS })
    //     })
    //         .then(response => response.json())
    //         .then(data => {
    //             if (data.status === 'ok') {
    //                 showNotification("Answers submitted successfully");
    //             } else {
    //                 showNotification("There was an error submitting your answers");
    //             }
    //         })
    //         .catch(error => {
    //             showNotification("There was an error submitting your answers");
    //         });
    // }

    function showNotification(message) {
        var notification = document.getElementById('notification');
        var messageElement = document.getElementById('notification-message');
        notification.style.display = 'flex';
        messageElement.innerHTML = message;
        notification.style.filter = 'opacity(1)';
    }

    function closeNotification() {
        var notification = document.getElementById('notification');
        notification.style.filter = 'opacity(0)';
        notification.style.display = 'none';
    }

    document.querySelector("#notification button").addEventListener('click', closeNotification);
});
