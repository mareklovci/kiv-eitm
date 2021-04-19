/* Script volající se po kliknutí na položku
    - Přechod ze stavu "loaded" do stavu "loading"
    - Přepnutí odkazu iframu
    - Aktivace buttonu "Přejít na stránku"
    - Přepnutí odkazu buttonu
*/

function loadIframe(url) {
    var $iframe = $('#' + "frame");
    var $link = $('#' + "go-to-page-link");
    var $iframeBackground = $('#' + "iframe-background");

    if ( $iframe.length ) {
        $iframe.attr('style', "display:none;");
        $iframe.attr('src', url);
        $link.attr('href', url);
        $link.attr('class', "btn btn-primary btn-lg mb-3 btn-block");
        $iframeBackground.attr('class', "loading");
        return false;
    }
    return true;
}

/* Script volající se po načtení iframe
    - Přechod ze stavu "loading" do stavu "loaded"
*/

function onLoadIframe() {
    var $iframeBackground = $('#' + "iframe-background");
    var $iframe = $('#' + "frame");

    $iframeBackground.attr('class', "loaded");
    $iframe.attr('style', "display:block;");
}
