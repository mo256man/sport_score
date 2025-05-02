setTimeout(() => {
    const btnVolley = document.getElementById("btnVolley");
    const btnHandball = document.getElementById("btnHandball");

    const eraseButtons = () => {
        [btnVolley, btnHandball].forEach(button => {
            button.style.backgroundColor="lightgray";
        });
    }

    const pushButton = (event) => {
        console.log("pushed");
        eraseButtons();
        event.target.style.backgroundColor = "lightgray";
    };

    btnVolley.addEventListener("click", pushButton);
    btnHandball.addEventListener("click", pushButton);
    pushButton(btnVolley);
}, 1000);
