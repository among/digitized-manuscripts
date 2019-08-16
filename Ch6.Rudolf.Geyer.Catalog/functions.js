// Copyright L.W. Cornelis van Lit, "The Digital Orientalist". For details see https://github.com/LWCvL/RudolfGeyerCatalog
// (f) = function, (e) = event

// 1. Initializing webapp
window.onload = function() {
  // setting initial variables
  searchData = catData;
  shadowCatalog = {};
  accentMap = {
    á: "a",
    à: "a",
    ā: "a",
    â: "a",
    ä: "ae",
    æ: "ae",
    é: "e",
    è: "e",
    ē: "e",
    ë: "e",
    í: "i",
    ì: "i",
    ī: "i",
    î: "i",
    y: "i",
    ó: "o",
    ò: "o",
    ō: "o",
    ô: "o",
    ö: "oe",
    ú: "u",
    ù: "u",
    ū: "u",
    û: "u",
    ü: "ue",
    ṭ: "t",
    ṣ: "s",
    ḍ: "d",
    ḥ: "h",
    ẓ: "z",
    ġ: "gh",
    š: "sh",
    ğ: "j",
    ḳ: "q",
    č: "ch",
    ʿ: "'",
    ʾ: "'",
    ".": " ",
    ",": " ",
    ":": " ",
    ";": " ",
    "?": " ",
    "!": " "
  };

  // Initial building of shadow catalog and interface
  Reducing_Catalogue(catData);
  Switch_Language("german");
};

// 2. Creating a shadow-catalog with simplified entries to easier match a search term in the search function
// Called by (e)window.onload
function Reducing_Catalogue(catalog) {
  // Looping through all catalogue entries
  for (var y = 0; y < catalog.length; y++) {
    // Adding all fields for each entry in one string.
    entryY = "";
    entryY += " " + catalog[y].title;
    entryY += " " + catalog[y].shortTitle;
    entryY += " " + catalog[y].publisher;
    entryY += " " + catalog[y]["publisher-place"];
    entryY += " " + Print_Names(catalog[y].author);
    entryY += " " + Print_Names(catalog[y].editor);
    entryY += " " + Print_Names(catalog[y].translator);
    entryY += " " + catalog[y].abstract;
    entryY += " " + catalog[y].language;
    // If field does not exist, 'undefined' will be pushed. All 'undefined's are now deleted.
    var definedY = entryY.replace(/undefined/g, "");
    // Entire string is stripped of transliteration marks, punctuation, capitals, and double spaces, and pushed into the shadow catalogue
    shadowCatalog[y] = Simplify_Term(definedY);
  }
}

// 3. Returning simplification of transliteration signs, punctuation, double spaces, and capitals
// Called by (f)Reducing_Catalogue and (f)Search_Catalog
function Simplify_Term(inputWord) {
  if (!inputWord) {
    return "";
  }
  inputLower = inputWord.toLowerCase();
  var outputWord = "";
  // Loop through every letter of a word
  for (var i = 0; i < inputLower.length; i++) {
    outputWord += accentMap[inputLower.charAt(i)] || inputLower.charAt(i);
  }
  returnedNoSpaces = outputWord.replace(/\s{2,}/g, " ");
  return returnedNoSpaces;
}

// 4. Switching interface to different language (currently German-English)
// Called by (e)window.onload and (e)flagTip.onclick
function Switch_Language(language) {
  // Array of words that are both keys to the texts-Object and elementIDs of the webapp
  toBeTranslated = Object.keys(texts);
  // Array which is agnostic as to how many/which languages there are
  languages = Object.keys(texts[toBeTranslated[0]]);
  // index number of current language
  lanIndex = languages.indexOf(language);

  if (lanIndex == languages.length - 1) {
    nextLanIndex = 0;
  } else {
    nextLanIndex = lanIndex + 1;
  }
  nextLanguage = languages[nextLanIndex];

  for (key in toBeTranslated) {
    // Filling different elements of webapp by their ID. Some need different ways of accessing their content.
    if (toBeTranslated[key].includes("Tip")) {
      document.getElementById(toBeTranslated[key]).title = Object.values(
        texts[toBeTranslated[key]]
      )[lanIndex];
    } else if (toBeTranslated[key] == "searchBox") {
      document.getElementById("searchTip").placeholder = Object.values(
        texts[toBeTranslated[key]]
      )[lanIndex];
    } else if (toBeTranslated[key].includes("Catalog")) {
      null;
    } else {
      document.getElementById(toBeTranslated[key]).innerHTML = Object.values(
        texts[toBeTranslated[key]]
      )[lanIndex];
    }
    // Setting button for switching language to the next one
    document.getElementById("flagTip").innerHTML =
      '<img src="iconflag' +
      nextLanguage +
      '.svg" height="16" width="32" class="flags" id="flagTip" )">';
    document.getElementById("flagTip").title = Object.values(texts.flagTip)[
      nextLanIndex
    ];
  }
  // Catalogue needs to be re-rendered
  if (document.getElementById("searchTip").value) {
    Search_Catalog(document.getElementById("searchTip").value);
  } else {
    Render_Table(catData, "beginTitleCatalog", lanIndex);
  }

  // Fancy mouse-over tool-tip only activitated when not on mobile. We simply delete previous instances and create new ones
  [...document.querySelectorAll("*")].forEach(node => {
    if (node._tippy) {
      node._tippy.destroy();
    }
  });
  if (
    /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ==
    false
  ) {
    tippy.setDefaults({
      animation: "perspective",
      arrow: "true",
      size: "large"
    });
    tippy("#flagTip", {
      content: Object.values(texts.flagTip)[nextLanIndex]
    });
    document.getElementById("flagTip").removeAttribute("title");
    tippy("#digitalOrientalistTip", {
      content: Object.values(texts.digitalOrientalistTip)[lanIndex]
    });
    document.getElementById("digitalOrientalistTip").removeAttribute("title");
    tippy("#stiftFlorianTip", {
      content: Object.values(texts.stiftFlorianTip)[lanIndex]
    });
    document.getElementById("stiftFlorianTip").removeAttribute("title");
    tippy("#searchTip", {
      content: Object.values(texts.searchTip)[lanIndex]
    });
    document.getElementById("searchTip").removeAttribute("title");    
  }
}
document.getElementById("flagTip").onclick = function() {
  Switch_Language(nextLanguage);
};

// 5. Rendering the table of catalogue entries
// Called by (f)Switch_Language and (f)Search_Catalog
function Render_Table(data, heading, language, numberEntries) {
  document.getElementById("catalogGeyer").innerHTML = "";
  htmlTableCat = '<table id="tableCatalog" class="table table-striped"><tbody>';
  for (i = 0; i < data.length; i++) {
    Render_Table_Entry(data, i, language);
  }

  htmlTableCat += "</tbody></table>";

  document.getElementById("catalogGeyer").innerHTML = htmlTableCat;
  if (typeof numberEntries !== "undefined") {
    document.getElementById("titleSearch").innerHTML =
      Object.values(texts[heading])[language] + " " + numberEntries;
  } else {
    document.getElementById("titleSearch").innerHTML = Object.values(
      texts[heading]
    )[language];
  }
}

// 6. Rendering one entry of the table
// Called by (f)Render_Table
function Render_Table_Entry(data, i, language) {
  var authorLan = Object.values(texts.authorCatalog)[language];
  var editorLan = Object.values(texts.editorCatalog)[language];
  var translatorLan = Object.values(texts.translatorCatalog)[language];
  var noAuthorLan = Object.values(texts.noAuthorCatalog)[language];

  htmlTableCat +=
    '<tr><td><div class="entry text text-left"><p class="text font-weight-bold"><svg onclick="Popup_More_Info(' +
    i +
    ", " +
    language +
    ')" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" width="15px" height="15px"><path class="iconModal" d="M25,2C12.297,2,2,12.297,2,25s10.297,23,23,23s23-10.297,23-23S37.703,2,25,2z M25,11c1.657,0,3,1.343,3,3s-1.343,3-3,3 s-3-1.343-3-3S23.343,11,25,11z M29,38h-2h-4h-2v-2h2V23h-2v-2h2h4v2v13h2V38z"/></svg> ' +
    data[i].title +
    '</p><p class="text-muted text font-weight-light">';
  // Cannot be sure if entry has an author, date, and place, so must check it first.
  if (data[i].hasOwnProperty("author")) {
    htmlTableCat += authorLan + Print_Names(data[i].author);
  } else {
    htmlTableCat += "<i>" + noAuthorLan + "</i>";
  }
  if (data[i].hasOwnProperty("editor")) {
    htmlTableCat += editorLan + Print_Names(data[i].editor);
  }
  if (data[i].hasOwnProperty("translator") == true) {
    htmlTableCat += translatorLan + Print_Names(data[i].translator);
  }
  htmlTableCat +=
    '</p></div></td><div class="entry text text-right"><td><p class="text blue">';
  if (data[i].issued) {
    htmlTableCat += data[i].issued["date-parts"];
  }
  htmlTableCat += "<br>";
  if (data[i]["publisher-place"]) {
    htmlTableCat += data[i]["publisher-place"];
  }
  htmlTableCat += "</p></div></td></tr>";
}

// 7. Generating more information on item in a pop-up
// Called by (f)Render_Table_Entry
function Popup_More_Info(number, language) {
  // For readability further on, these variables are defined here.
  var authorLan = Object.values(texts.authorCatalog)[language];
  var editorLan = Object.values(texts.editorCatalog)[language];
  var translatorLan = Object.values(texts.translatorCatalog)[language];
  var noAuthorLan = Object.values(texts.noAuthorCatalog)[language];
  var numberVolumesLan = Object.values(texts.numberVolumesCatalog)[language];
  var publisherLan = Object.values(texts.publisherCatalog)[language];
  var placeLan = Object.values(texts.placeCatalog)[language];
  var yearLan = Object.values(texts.yearCatalog)[language];
  var additionalLan = Object.values(texts.additionalCatalog)[language];
  var callNumberLan = Object.values(texts.callNumberCatalog)[language];
  var urlLan = Object.values(texts.urlCatalog)[language];
  var closeLan = Object.values(texts.closeCatalog)[language];

  // The div already declared in the HTML is popupInfo, the div dynamically created is popupModalInfo. All of the dynamic html is inserted in popupInfo, and then popupModalInfo is made into a modal (pop-up) wih the package MicroModal.

  htmlPopupInfo =
    "<div class='modal micromodal-slide' id='popupModalInfo' aria-hidden='true'>" +
    "<div class='modal__overlay' tabindex='-1' data-micromodal-close>" +
    "<div class='modal__container' role='dialog' aria-modal='true' aria-labelledby='modal-1-title'>" +
    "<header class='modal__header'>" +
    "<h3 class='headline' id='modal-1-title'>" +
    searchData[number].title +
    "</h3>" +
    "<button class='modal__close' aria-label='Close modal' data-micromodal-close></button>" +
    "</header>" +
    "<main class='modal__content' id='modal-1-content'>" +
    "<p>";

  if (searchData[number].hasOwnProperty("shortTitle")) {
    htmlPopupInfo += "<i>" + searchData[number].shortTitle + "</i><br>";
  }
  if (searchData[number].hasOwnProperty("author")) {
    htmlPopupInfo +=
      authorLan + Print_Names(searchData[number].author) + "<br>";
  }
  if (searchData[number].hasOwnProperty("editor")) {
    htmlPopupInfo +=
      editorLan + Print_Names(searchData[number].editor) + "<br>";
  }
  if (searchData[number].hasOwnProperty("translator")) {
    htmlPopupInfo +=
      translatorLan + Print_Names(searchData[number].translator) + "<br>";
  }
  if (
    searchData[number].hasOwnProperty("author") == false &&
    searchData[number].hasOwnProperty("editor") == false &&
    searchData[number].hasOwnProperty("translator") == false
  ) {
    htmlPopupInfo += noAuthorLan + "<br>";
  }
  if (searchData[number].hasOwnProperty("number-of-volumes")) {
    htmlPopupInfo +=
      numberVolumesLan + searchData[number]["number-of-volumes"] + "<br>";
  }
  if (searchData[number].hasOwnProperty("publisher")) {
    htmlPopupInfo += publisherLan + searchData[number].publisher + "<br>";
  }
  if (searchData[number].hasOwnProperty("publisher-place")) {
    htmlPopupInfo += placeLan + searchData[number]["publisher-place"] + "<br>";
  }
  if (searchData[number].hasOwnProperty("issued")) {
    htmlPopupInfo += yearLan + searchData[number].issued["date-parts"][0][0];
  }
  if (searchData[number].hasOwnProperty("abstract")) {
    htmlPopupInfo +=
      '<hr><p class="text-success"><b>' +
      additionalLan +
      "</b><br>" +
      searchData[number].abstract +
      "</p>";
  }
  if (searchData[number].hasOwnProperty("language")) {
    htmlPopupInfo +=
      "<hr>" +
      callNumberLan +
      searchData[number].language +
      " (" +
      searchData[number].type +
      ")<br>";
  }
  if (searchData[number].hasOwnProperty("URL")) {
    htmlPopupInfo +=
      '<a href="' +
      searchData[number].URL +
      '" target="_blank">' +
      urlLan +
      "</a><br>";
  }
  htmlPopupInfo +=
    "</p>" +
    "<button class='btn-blue' data-micromodal-close aria-label='Close this dialog window'>" +
    closeLan +
    "</button>" +
    "</main>" +
    "</div>" +
    "</div>" +
    "</div>";

  document.getElementById("popupInfo").innerHTML = htmlPopupInfo;
  MicroModal.init({
    openTrigger: "data-custom-open",
    closeTrigger: "data-custom-close",
    disableScroll: true,
    disableFocus: false,
    awaitCloseAnimation: true,
    debugMode: true
  });
  MicroModal.show("popupModalInfo");
}

// 8. Returning all the names for a given category and prints them in the format 'first' - 'preposition' - 'last'.
// Called by (f)Render_Table_Entry and (f)Popup_More_Info
function Print_Names(entry) {
  if (!entry) {
    return;
  }
  // This will be the container for all names. Note that in any category (author, editor, translator) there could be multiple persons and each person's name consist of several elements
  namesString = "";

  // We are aiming here for a formatting of FIRSTNAME-PREPOSITION-LASTNAME. Further, persons are separated by a comma and the whole list ends with a period.
  for (var name = 0; name < entry.length; name++) {
    if (entry[name]["given"]) {
      namesString += entry[name]["given"];
    }
    if (entry[name].hasOwnProperty("non-dropping-particle")) {
      namesString += " " + entry[name]["non-dropping-particle"];
    }
    namesString += " " + entry[name]["family"];
    if (name == entry.length - 1) {
      namesString += ". ";
    } else {
      namesString += ", ";
    }
  }
  return namesString;
}

// 9. Searching keyword and showing results
// Variously called to initiate search (clicking button or hitting Enter) or re-render catalog (if order is changed)
function Search_Catalog(input) {
  // Final result will be a subset of the catalog
  searchData = [];
  // We will not compare search term with catalog, but simplified version of search term with shadow catalog.
  normalizedInput = Simplify_Term(input);
  for (i = 0; i < catData.length; i++) {
    if (shadowCatalog[i].includes(normalizedInput)) {
      searchData.push(catData[i]);
    }
  }

  // Analyze resulting subset; if zero, render entire catalog with heading title 'no results'
  if (searchData.length == 0) {
    Render_Table(catData, "noResultsTitleCatalog", lanIndex);
  } else {
    Render_Table(searchData, "foundItemsCatalog", lanIndex, searchData.length);
  }
}
document.getElementById("searchTip").addEventListener("keyup", function(event) {
  event.preventDefault();
  // 13 is 'Enter'-key
  if (
    event.keyCode === 13 &&
    document.getElementById("searchTip").value != ""
  ) {
    Search_Catalog(document.getElementById("searchTip").value);
    // If user deletes search term, render entire catalog again
  } else if (document.getElementById("searchTip").value == "") {
    Render_Table(catData, "againTitleCatalog", lanIndex);
  }
});
document.getElementById("searchButton").onclick = function() {
  if (document.getElementById("searchTip").value != "") {
    Search_Catalog(document.getElementById("searchTip").value);
  }
};

// 10. Sort and render search results or entire catalog by title, putting empty titles at the top
// Called by (e)sortTitleCaption.click
function Indexing_Title_Catalog() {
  catData.sort(function(a, b) {
    if (a.hasOwnProperty("title")) {
      firstTitle = a.title;
    } else {
      firstTitle = "";
    }
    if (b.hasOwnProperty("title")) {
      secondTitle = b.title;
    } else {
      secondTitle = "";
    }
    return firstTitle.toLowerCase().localeCompare(secondTitle.toLowerCase());
  });
  // New shadow catalog is necessary, to keep actual and shadow catalog in same order
  Reducing_Catalogue(catData);
}
document
  .getElementById("sortTitleCaption")
  .addEventListener("click", function() {
    Indexing_Title_Catalog();
    if (document.getElementById("searchTip").value != "") {
      // This ensures only the search results are shown when ordering
      Search_Catalog(document.getElementById("searchTip").value);
    } else {
      Render_Table(catData, "beginTitleCatalog", lanIndex);
    }
  });

// 11. Sort and render search results or entire catalog by author. If no author, then editor or translator. Empty ones put at top.
// Called by (e)sortAuthorCaption.click
function Indexing_Author_Catalog() {
  catData.sort(function(a, b) {
    if (a.hasOwnProperty("author")) {
      firstAuthor = a.author[0]["family"];
    } else if (a.hasOwnProperty("editor")) {
      firstAuthor = a.editor[0]["family"];
    } else if (a.hasOwnProperty("translator")) {
      firstAuthor = a.translator[0]["family"];
    } else {
      firstAuthor = "";
    }
    if (b.hasOwnProperty("author")) {
      secondAuthor = b.author[0]["family"];
    } else if (b.hasOwnProperty("editor")) {
      secondAuthor = b.editor[0]["family"];
    } else if (b.hasOwnProperty("translator")) {
      secondAuthor = b.translator[0]["family"];
    } else {
      secondAuthor = "";
    }
    return firstAuthor.toLowerCase().localeCompare(secondAuthor.toLowerCase());
  });
  // New shadow catalog is necessary, to keep actual and shadow catalog in same order
  Reducing_Catalogue(catData);
}
document
  .getElementById("sortAuthorCaption")
  .addEventListener("click", function() {
    Indexing_Author_Catalog();
    if (document.getElementById("searchTip").value != "") {
      // This ensures only the search results are shown when ordering
      Search_Catalog(document.getElementById("searchTip").value);
    } else {
      Render_Table(catData, "beginTitleCatalog", lanIndex);
    }
  });

// 12. Sort and render search results or entire catalog by year, putting empty years at the top
// Called by (e)sortYearCaption.click
function Indexing_Year_Catalog() {
  catData.sort(function(a, b) {
    if (a.hasOwnProperty("issued")) {
      // Invariably, if there is an 'issued' key, then the actual year is stored two levels deeper
      firstYear = a.issued["date-parts"][0][0];
    } else {
      firstYear = "0";
    }
    if (b.hasOwnProperty("issued")) {
      secondYear = b.issued["date-parts"][0][0];
    } else {
      secondYear = "0";
    }
    return parseInt(firstYear) - parseInt(secondYear);
  });
  // New shadow catalog is necessary, to keep actual and shadow catalog in same order
  Reducing_Catalogue(catData);
}
document
  .getElementById("sortYearCaption")
  .addEventListener("click", function() {
    Indexing_Year_Catalog();
    if (document.getElementById("searchTip").value != "") {
      // This ensures only the search results are shown when ordering
      Search_Catalog(document.getElementById("searchTip").value);
    } else {
      Render_Table(catData, "beginTitleCatalog", lanIndex);
    }
  });
