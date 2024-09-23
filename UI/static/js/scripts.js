document.addEventListener('DOMContentLoaded', () => {
    const chapterSelect = document.getElementById('chapter-select');
    const pdfViewer = document.getElementById('pdf-viewer');
    const prevButton = document.getElementById('prev-chapter');
    const nextButton = document.getElementById('next-chapter');
    const toggleModeButton = document.getElementById('toggle-mode');
    const chooseFolderButton = document.getElementById('choose-folder');
    const hidePanelButton = document.getElementById('hide-panel');
    const showPanelButton = document.getElementById('show-panel');
    const folderName = document.getElementById('folder-name');
    const toggleInput = document.getElementById('toggle-mode-input');

    let currentChapter = 0;
    let chapters = [];
    let darkMode = false;
    let mangaFolder = '';

    // Load last viewed chapter, folder, and dark mode state
    fetch('/load-settings')
        .then(response => response.json())
        .then(data => {
            if (data.folder) {
                mangaFolder = data.folder;
                folderName.textContent = mangaFolder.split('/').pop();
                loadFolder(mangaFolder, data.chapter); // Pass the saved chapter index here
            }
            darkMode = data.dark_mode || false;
            applyDarkMode(darkMode);
        });

    chooseFolderButton.addEventListener('click', () => {
        fetch('/choose-folder')
            .then(response => response.json())
            .then(data => {
                chapters = data.chapters;
                mangaFolder = data.folder;
                folderName.textContent = mangaFolder.split('/').pop();
                chapters = sortChapters(chapters);  // Sort the chapters before loading
                loadChapterByName(chapters[0]);  // Load the first chapter by name initially after folder selection
                saveSettings();  // Save the settings with the initial chapter
            })
            .catch(error => {
                console.error('Error:', error.message);
                alert('No folder was selected. Please choose a folder.');
            });
    });

    chapterSelect.addEventListener('change', () => {
        const selectedChapter = chapterSelect.value;  // Get the selected chapter name
        loadChapterByName(selectedChapter);  // Load the chapter by its name
        saveSettings();  // Save the current state after selecting a chapter
    });

    prevButton.addEventListener('click', () => {
        if (currentChapter > 0) {
            currentChapter--;
            loadChapterByName(chapters[currentChapter]);  // Load the previous chapter by its name
            chapterSelect.value = chapters[currentChapter];  // Update the dropdown to match the loaded chapter
            saveSettings();
        }
    });

    nextButton.addEventListener('click', () => {
        if (currentChapter < chapters.length - 1) {
            currentChapter++;
            loadChapterByName(chapters[currentChapter]);  // Load the next chapter by its name
            chapterSelect.value = chapters[currentChapter];  // Update the dropdown to match the loaded chapter
            saveSettings();
        }
    });

    toggleModeButton.addEventListener('click', () => {
        darkMode = !darkMode;
        applyDarkMode(darkMode);
        saveSettings();
    });

    // Hiding the panel by default and showing it on hover button click
    hidePanelButton.addEventListener('click', () => {
        document.getElementById('controls').classList.add('hidden');
        pdfViewer.style.flex = '1';
        showPanelButton.classList.add('visible');
    });

    showPanelButton.addEventListener('click', () => {
        document.getElementById('controls').classList.remove('hidden');
        pdfViewer.style.flex = '1';
        showPanelButton.classList.remove('visible');
    });

    function applyDarkMode(isDark) {
        document.body.classList.toggle('dark-mode', isDark);
        toggleModeButton.querySelector('img').src = isDark ? '/static/images/light_mode.png' : '/static/images/dark_mode.png';
        toggleInput.checked = isDark;
        prevButton.querySelector('img').src = isDark ? '/static/images/dark_prev.png' : '/static/images/light_prev.png';
        nextButton.querySelector('img').src = isDark ? '/static/images/dark_next.png' : '/static/images/light_next.png';
    }

    function loadChapterByName(chapterName) {
        currentChapter = chapters.indexOf(chapterName);  // Update the currentChapter based on the name
        fetch(`/chapter/${chapterName}`)
            .then(response => response.blob())
            .then(blob => {
                const url = URL.createObjectURL(blob);
                pdfViewer.innerHTML = `<embed src="${url}#page=1" type="application/pdf" width="100%" height="100%">`;
            });
    }

    function loadFolder(folder, chapterIndex) {
        fetch(`/load-folder?folder=${encodeURIComponent(folder)}`)
            .then(response => response.json())
            .then(data => {
                chapters = sortChapters(data);
                chapterSelect.innerHTML = '';
                chapters.forEach((chapterName) => {
                    const option = document.createElement('option');
                    option.value = chapterName;
                    option.textContent = chapterName;
                    chapterSelect.appendChild(option);
                });
                // Load the saved or specified chapter
                const chapterName = chapters[chapterIndex] || chapters[0];  // Use the saved chapter or the first one
                loadChapterByName(chapterName);
                chapterSelect.value = chapterName;  // Set dropdown value to the loaded chapter
            });
    }

    // Function to save settings (including dark mode state)
    function saveSettings() {
        fetch('/save-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                folder: mangaFolder,
                chapter: currentChapter,
                dark_mode: darkMode
            })
        });
    }

    // Function to sort chapters based on the first and second numbers in the file name
    function sortChapters(chapters) {
        return chapters.sort((a, b) => {
            const extractNumbers = (str) => {
                const match = str.match(/(\d+)(-\d+)?/);
                if (match) {
                    const firstNum = parseInt(match[1], 10);
                    const secondNum = match[2] ? parseInt(match[2].slice(1), 10) : 0;
                    return [firstNum, secondNum];
                }
                return [0, 0];  // No number found
            };

            const [numA1, numA2] = extractNumbers(a);
            const [numB1, numB2] = extractNumbers(b);

            if (numA1 === numB1) {
                return numA2 - numB2;
            }
            return numA1 - numB1;
        });
    }

    // Hide the control panel on load
    document.getElementById('controls').classList.add('hidden');
    showPanelButton.classList.add('visible');  // Show the ">" button to open the panel
});


document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('#controls button, #controls select, #nav-buttons button, #choose-folder, #toggle-mode');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            // Add the 'clicked' class to make the background red
            button.classList.add('clicked');

            // Remove the 'clicked' class after 150 milliseconds to revert to original color
            setTimeout(() => {
                button.classList.remove('clicked');
            }, 250); // Adjust this value to control the red background duration
        });
    });
});
