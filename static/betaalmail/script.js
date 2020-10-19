function openQuery(query, el) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName('tabcontent');
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = 'none';
        }
    tablinks = document.getElementsByClassName('tablink');
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].style.backgroundColor = '';
        tablinks[i].style.color = 'white';
        }
    document.getElementById(query).style.display = 'block';
    el.style.backgroundColor = 'white';
    el.style.color = 'black';
    };

function copyStringToClipboard (str, id) {
    document.getElementById(id).style.color = "lightgray";
    // Create new element
    var el = document.createElement('textarea');
    // Set value (string to be copied)
    el.value = str;
    // Set non-editable to avoid focus and move outside of view
    el.setAttribute('readonly', '');
    el.style = {position: 'absolute', left: '-9999px'};
    document.body.appendChild(el);
    // Select text inside element
    el.select();
    // Copy text to clipboard
    document.execCommand('copy');
    // Remove temporary element
    document.body.removeChild(el);
    };

function shutDown() {
    $.get('/shutdown', function() {
            window.open('','_self').close();
            return;
        });
    };
