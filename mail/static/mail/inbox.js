document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // submit email
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-detail-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-detail-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // get emails data
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {

      //create table
      const mail_table = document.createElement('table');
      document.querySelector('#emails-view').append(mail_table);

      // ... do something else with email ...
      emails.forEach(single_email => {
        const new_email = document.createElement('tr');
        if (single_email.read === true) {
          new_email.className = "read_email";
        } else {
          new_email.className = "unread_email";
        }
        
        new_email.innerHTML = `
          <td class='sender_col'>${single_email.sender}</td>
          <td class='subject_col'>Subject: ${single_email.subject}</td>
          <td class='time_col'>${single_email.timestamp}</td>
        `;

        // bg color follow its class
        // new_email.className = single_email.read ? 'read': 'unread';
        new_email.addEventListener('click', function() {
            console.log('This element has been clicked!');
            view_email(single_email.id);
        });
        mail_table.append(new_email);
        
      });
  });
}

function send_email(event) {
  event.preventDefault();

  // collect data
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // send data
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
      load_mailbox('sent');
  });
}

function view_email(email_id) {
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {

      // Show the mailbox and hide other views
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'none';
      document.querySelector('#email-detail-view').style.display = 'block';

      let body_message = email.body.replace(/\r?\n/g,'<br/>');

      document.querySelector('#email-detail-view').innerHTML = `
      
        <div class='email_head'>
            <strong>From:</strong> ${email.sender}<br/>
            <strong>To:</strong> ${email.recipients}<br/>
            <strong>Subject:</strong> ${email.subject}<br/>
            <strong>Timestamp:</strong> ${email.timestamp}
        </div>
        <div class='email_body'>${body_message}</div>
      
      `

      // change read status
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          read: true
        })
      })

      // button container
      const btn_container = document.createElement('div');
      btn_container.className = 'btn_container';

      // reply
      const reply_btn = document.createElement('button');
      reply_btn.innerHTML = 'Reply';
      reply_btn.className = 'btn btn-sm btn-outline-primary';
      reply_btn.addEventListener('click', function() {
        compose_email();
        // prefill
        document.querySelector('#compose-recipients').value = email.sender;
        document.querySelector('#compose-body').value = '\n-----------------------------------------\n'
        + `On ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
        let subject = email.subject;
        if (subject.split(':')[0] != 'Re') {
          subject = 'Re: ' + subject;
        }
        document.querySelector('#compose-subject').value = subject;

      });
      btn_container.append(reply_btn);

      // archived status
      const archived_btn = document.createElement('button');
      archived_btn.innerHTML = email.archived ? 'Unarchived': 'Archives';
      archived_btn.className = email.archived ? 'btn btn-sm btn-outline-danger': 'btn btn-sm btn-outline-success';
      archived_btn.addEventListener('click', function() {
        fetch(`/emails/${email_id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: !email.archived
          })
        })
        .then(() => {load_mailbox('archive')})
      });
      btn_container.append(archived_btn);

      document.querySelector('#email-detail-view').append(btn_container);
  });
}