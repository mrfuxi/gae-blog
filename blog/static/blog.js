$(function() {
    $("#post_form_container .btn-open").click(toggle_form);
    $("#post_form_container .btn-close").click(toggle_form);
    $("#post_form_container .btn-delete").click(delete_post);
    $("#post_form").submit(submit_post);
});

function toggle_form() {
    var container = $("#post_form_container");
    var article = $("article.post");
    var form = container.find("form");

    form.find(".form_error").hide();
    form.find(".form_error").empty();
    form.trigger("reset");
    container.toggleClass("form_hidden");
    article.toggle(container.hasClass("form_hidden"));

    if (article.length == 1 && !container.hasClass("form_hidden")) {
        form.find(":input").each(function() {
            var article_field = article.find(".post_" + this.name);
            if (article_field.length == 1) {
                this.value = article_field.text().trim();
            }
        })
    }
}

function submit_post(event) {
    var form = $(event.target);
    event.preventDefault();

    var request = $.ajax({
        url: form.attr("action"),
        type: "POST",
        data: form.serialize(),
    });

    request.done(function (data, status, xhr) {
        var list_of_articles = $("#article_list");
        var article = $("article.post");

        if (list_of_articles.length == 1) {
            list_of_articles.prepend(data);
        } else if (article.length == 1) {
            article.html(data);
        }

        form.trigger("reset");
        form.find(".form_error").empty();
        form.find(".form_error").hide();
        toggle_form();
    })

    request.fail(function (xhr, status) {
        var error_info = form.find(".form_error")
        error_info.show();
        error_info.html(xhr.responseText);
    })
}

function delete_post() {
    var data = {
        "csrfmiddlewaretoken": $('form :input[name=csrfmiddlewaretoken]').val(),
    }

    var headers = {
        "X-CSRFToken": $('form :input[name=csrfmiddlewaretoken]').val(),
    }

    var request = $.ajax({
        url: ".",
        type: "DELETE",
        headers: headers,
    });

    request.done(function (data, status, xhr) {
        window.location.href = "/";
    });
}
