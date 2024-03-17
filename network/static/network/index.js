document.addEventListener('DOMContentLoaded', function() {
    const follow_btn = document.querySelector('#follow_btn');
    if (follow_btn) {
        follow_btn.addEventListener('click', toggle_follow);
    };

    document.querySelectorAll('.edit_btn').forEach(button => {
        button.onclick = function() {
            // button == document.activeElement;
            show_edit_box(button.value);
        };
    });

});

function show_edit_box(post_id) {
    console.log("click");
    console.log(post_id);
    const post_container = document.querySelector(`#post_message_container_${post_id}`);
    const message = document.querySelector(`#message_${post_id}`).innerHTML;
    const edit_btn = document.querySelector(`#edit_btn_${post_id}`);

    // hide edit btn and post messsage
    edit_btn.style.display = 'none';
    document.querySelector(`#message_${post_id}`).style.display = 'none';

    // Create new
    const edit_container = document.createElement('div');
    edit_container.id = `edit_container_post_${post_id}`;

    const edit_area = document.createElement('textarea');
    edit_area.id = `edit_message_post_${post_id}`
    edit_area.className = "edit_area"
    edit_area.innerHTML = message;
    edit_container.append(edit_area);

    const save_btn = document.createElement('button');
    save_btn.className = "save_btn"
    save_btn.innerHTML = "Save"
    save_btn.onclick = function() {
        save_post(post_id)
    };
    edit_container.append(save_btn);
    
    // Add to DOM
    post_container.append(edit_container);
}

function save_post(post_id) {
    console.log(`save post ${post_id}`);
    const post_message = document.querySelector(`#edit_message_post_${post_id}`).value;
    console.log(post_message)
    fetch("/edit_post", {
        method: 'PUT',
        body: JSON.stringify({
            post_id: post_id,
            post_message: post_message,
        })
    })
    .then(response => {
        if (response.ok) {
            console.log('Data updated successfully');
            const post_container = document.querySelector(`#post_message_container_${post_id}`);
            const message = document.querySelector(`#message_${post_id}`);
            const edit_btn = document.querySelector(`#edit_btn_${post_id}`);
            const edit_container = document.querySelector(`#edit_container_post_${post_id}`);
            message.innerHTML = post_message;
            message.style.display = 'block';
            edit_btn.style.display = 'block';
            edit_container.remove();
        } else {
            console.error('Failed to update data');
            // Handle error, if needed
        }
    })
}


function toggle_follow() {
    // edit Follower database
    fetch('/follow', {
        method: 'POST',
        body: JSON.stringify({
            followed_user_id: this.value,
            follow_action: this.innerHTML,
        })
        })
        .then(response => response.json())
        .then(result => {
            // update follow amount
            const following_display = document.querySelector('#following');
            const follower_display = document.querySelector('#follower');
            following_display.innerHTML = `<h6>Following: ${ result.following_count }</h6>`;
            follower_display.innerHTML = `<h6>Follower: ${ result.follower_count }</h6>`;
    });

    // change follow button ui
    if (this.innerHTML === "Follow") {
        this.innerHTML = "Unfollow";
        this.className = "btn btn-danger";
    } else {
        this.innerHTML = "Follow";
        this.className = "btn btn-primary";
    }

}