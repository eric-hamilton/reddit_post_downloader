function grabRedditLinks(clearClipboard = true) {
  var currentUrl = window.location.href;
  var regex = /https:\/\/www\.reddit\.com\/r\/([^/]+)\/comments\/([^/]+)\/([^/]+)\/(?!comment\/)/g;

  var links = document.querySelectorAll('a[href*="/comments"]');
  var matchedLinks = new Set();

  links.forEach(link => {
    var href = link.href;
    var match = regex.exec(href);

    if (match) {
      var linkUrl = match[0].split('?')[0];
      matchedLinks.add(linkUrl);
    }

    if (regex.exec(currentUrl)) {
      matchedLinks.add(currentUrl);
    }

  });

  if (clearClipboard) {

    var uniqueLinksArray = Array.from(matchedLinks);
    navigator.clipboard.writeText(uniqueLinksArray.join('\n'))
      .then(() => {
        console.log('Links copied to clipboard!');
        alert(uniqueLinksArray.length + " links copied to clipboard!");
      })
      .catch((error) => {
        console.error('Failed to copy links to clipboard:', error);
        alert("An error occurred while copying links.");
      });

  } else {

    navigator.clipboard.readText().then((clipboardContents) => {

      var existingLinks = new Set(clipboardContents.split("\n"));

      matchedLinks.forEach(link => existingLinks.add(link));

      var updatedClipboardContents = Array.from(existingLinks).join('\n');

      navigator.clipboard.writeText(updatedClipboardContents)
        .then(() => {
          console.log('Links appended to clipboard!');
          alert(matchedLinks.size + " links appended to clipboard!");
        })
        .catch((error) => {
          console.error('Failed to append links to clipboard:', error);
          alert("An error occurred while appending links.");
        });
    }).catch((error) => {
      console.error('Failed to read clipboard:', error);
      alert("An error occurred while reading the clipboard.");
    });
  }
}

function grabSingleLink(linkUrl, clearClipboard = true) {
  var regex = /https:\/\/www\.reddit\.com\/r\/([^/]+)\/comments\/([^/]+)\/([^/]+)\/(?!comment\/)/g;

  var match = regex.exec(linkUrl);
  if (match) {
     linkUrl = match[0].split('?')[0];
     
     if (clearClipboard) {
         navigator.clipboard.writeText(linkUrl)
         .then(() => {
            console.log('Link copied to clipboard!');
            alert("Link copied to clipboard!");
          })
          .catch((error) => {
            console.error('Failed to copy link to clipboard:', error);
            alert("An error occurred while copying link.");
          });
         
     } else {
         navigator.clipboard.readText().then((clipboardContents) => {
          var existingLinks = new Set(clipboardContents.split("\n"));
          existingLinks.add(linkUrl);
          var updatedClipboardContents = Array.from(existingLinks).join('\n');
          navigator.clipboard.writeText(updatedClipboardContents)
            .then(() => {
              console.log('Link appended to clipboard!');
              alert("Link appended to clipboard!");
            })
            .catch((error) => {
              console.error('Failed to append link to clipboard:', error);
              alert("An error occurred while appending link.");
            });
        }).catch((error) => {
          console.error('Failed to read clipboard:', error);
          alert("An error occurred while reading the clipboard.");
        });
     }
  }
}


function manageContextMenus(info, tab) {

  switch (info.menuItemId) {

    case 'pageLinkGrabberAppend':
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: grabRedditLinks,
        args: [false] // Don't Clear Clipboard
      });
      console.log('pageLinkGrabberAppend');
      break;

    case 'pageLinkGrabberOverwrite':
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: grabRedditLinks,
        args: [true] // Clear Clipboard
      });
      console.log('pageLinkGrabberOverwrite');
      break;

    case 'linkGrabberAppend':
      var linkUrl = info.linkUrl
      console.log(linkUrl);
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: grabSingleLink,
        args: [linkUrl, false] // Don't Clear Clipboard
      });
      console.log('linkGrabberAppend');
      break;

    case 'linkGrabberOverwrite':
      var linkUrl = info.linkUrl
      console.log(linkUrl);
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: grabSingleLink,
        args: [linkUrl, true] // Clear Clipboard
      });
      console.log('linkGrabberOverwrite');
      break;
  }
}

chrome.runtime.onInstalled.addListener(function () {
  //contexts:
    //'page'
    //'selection'
    //'link'
    //'editable'
    //'image',
    //'video'
    //'audio'

  chrome.contextMenus.create({
    title: 'Add all page links to clipboard',
    id: 'pageLinkGrabberAppend',
    contexts: ["page"]
  });

  chrome.contextMenus.create({
    title: 'Clear clipboard and add all page links',
    id: 'pageLinkGrabberOverwrite',
    contexts: ["page"]
  });

  chrome.contextMenus.create({
    title: 'Add post link to clipboard',
    id: 'linkGrabberAppend',
    contexts: ["link", "image", "video"]
  });

  chrome.contextMenus.create({
    title: 'Clear the clipboard and add this link',
    id: 'linkGrabberOverwrite',
    contexts: ["link", "image", "video"]
  });

});

// Listener to pipe context menus to the management function
chrome.contextMenus.onClicked.addListener(manageContextMenus);

// Default Functionality when extension icon is clicked
chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: grabRedditLinks
  });
});


