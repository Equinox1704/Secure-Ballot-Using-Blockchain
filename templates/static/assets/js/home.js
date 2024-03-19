function openSection(sectionId) {
    // Hide all sections
    $('#dashboard, #history, #settings, #contact, #profile').hide();
    // Show the selected section
    $('#' + sectionId).show();

    // Call fetchProfileData function if the profile section is opened
    if (sectionId === 'profile') {
        const uniqueAddress = $('.unique-address').text();
        fetchProfileData(uniqueAddress);
    }
}

function toggleDarkMode() {
    if ($('#darkMode').text() === 'Dark Mode') {
        $('body').css('background-color', '#343a40');
        $('#sidebar').css('background-color', '#212529');
        $('#sidebar, #main-content').css('color', 'white');
        $('#darkMode').text('Light Mode');
    } else {
        $('body').css('background-color', '#f8f9fa');
        $('#sidebar').css('background-color', '#343a40');
        $('#sidebar, #main-content').css('color', 'black');
        $('#darkMode').text('Dark Mode');
    }
}

function showPopup(eventName) {
    console.log("Showing popup for event:", eventName); // Debugging statement

    // Show the popup window
    $('#popup-window').show();

    // Clear previous content
    $('#popup-content').empty();

    // Fetch event data from session request

    if (eventName === 'Harmony Poll: The Ayodhya Accord') {
        // Predefined content
        $('#popup-content').html(`
            <h2>${eventName}</h2>
            <div class="event-details">
                <p>
                    The Harmony Poll: The Ayodhya Accord aims to engage the community in a constructive dialogue, fostering a spirit of reconciliation and collective decision-making regarding the development of the Ayodhya site. It’s a platform for people to voice their opinions and vote on proposals that honor the diverse cultural and historical significance of the location, while looking forward to a peaceful and inclusive future.
                </p>
                <div class="event-images">
                    <img src="/static/assets/img/ram_mandir.jpg" alt="Ram Mandir" style="float: left; margin-right: 10px;">
                    <img src="/static/assets/img/babri_masjid.jpg" alt="Babri Masjid" style="float: right; margin-left: 10px;">
                </div>
                <div style="clear: both;"></div>
                <div class="vote-options">
                    <button id="vote-for">Vote</button>
                    <button id="vote-against">Vote</button>
                </div>
                <div id="result" style="text-align: center;">
                    <h3>Result</h3>
                    <p>Ram Mandir - 100 votes</p>
                    <p>Babri Masjid - 1 vote</p>
                    <p>Winner - Ram Mandir</p>
                </div>
            </div>
        `);
        // Disable vote buttons and show alert on click
        $('#vote-for').click(function() {
            alert('Event has ended');
        });

        $('#vote-against').click(function() {
            alert('Event has ended');
        });
    }
}

function filterAndShowPopups(eventName, eventId, eventPurpose, teamsDataScript) {
    // Parse the teams data from the script element
    var teamsData = JSON.parse(teamsDataScript.textContent);

    // Filter out the teams data for the clicked event ID
    var teamsForEvent = teamsData[eventId];

    // Pass the filtered teams data to the showPopups function
    showPopups(eventName, eventId, eventPurpose, teamsForEvent);
}

function showPopups(eventName, eventId, eventPurpose, teamsData) {
    console.log("Showing popup for event:", eventName); // Debugging statement

    // Show the popup window
    $('#popup-container').show();

    // Set event data in the popup
    $('#popup-event-name').text(eventName);
    $('#popup-event-id').text(eventId);
    $('#popup-event-purpose').text(eventPurpose);

    // Populate teams data
    var teamContainer = $('#team-container');
    teamContainer.empty();

    // Iterate over the filtered teams data and add them to the team container
    teamsData.forEach(function(team) {
        var teamElement = $('<div class="team">');
        teamElement.append('<h3>' + team.fields.name + '</h3>');
        teamElement.append('<img src="' + team.fields.image + '" alt="' + team.fields.name + '">');
        teamContainer.append(teamElement);
    });
}


function hidePopup() {
    document.getElementById('popup-container').style.display = 'none';
}

function loadEvents() {
    const pastEvents = [
        'Harmony Poll: The Ayodhya Accord'
    ];

    // Display past events
    const $pastEvents = $('#past-events');
    pastEvents.forEach(event => {
        $pastEvents.append(`<div class="event-block" onclick="showPopup('${event}')">${event}</div>`);
    });
}

// Call loadEvents function when the page loads
$(document).ready(function() {
    loadEvents();
});

function closePopup() {
    // Hide the popup window
    $('#popup-window').hide();
}

function voteFor(eventName) {
    // Handle voting for the specified event (e.g., increment vote count)
    console.log('Voted for ' + eventName);
}

function voteAgainst(eventName) {
    // Handle voting against the specified event (e.g., decrement vote count)
    console.log('Voted against ' + eventName);
}
