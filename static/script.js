const btnVolley = $("#btn_volley");
const btnHandball = $("#btn_handball");
const btnBaseball = $("#btn_baseball");


const eraseButtons = () => {
    [btnVolley, btnHandball, btnBaseball].forEach(button => {
        button.css("background-color", "lightgray");
    });
}

const pushButton = async function(){
    eraseButtons();
    const id = $(this).attr("id");
    $("#" + id).css("background-color", "lightcyan");
    await sendData(id);
};

const sendData = async (id) => {
    $.ajax({
        url: "/select_game",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ key: id })
    }).done( (response) => {
        $("#game").text(response.game)
        console.log("Flaskからのレスポンス:", response);
    }).fail( (xhr, status, error) => {
            console.error("エラー:", error);
    });
}

btnVolley.on("click", pushButton);
btnHandball.on("click", pushButton);
btnBaseball.on("click", pushButton);
eraseButtons();