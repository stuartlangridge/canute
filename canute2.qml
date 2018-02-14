import QtQuick 2.5
import QtQuick.Controls 1.0
import QtQuick.Window 2.0
import QtGraphicalEffects 1.0

ApplicationWindow {
    id : root
    visible: false
    width: Screen.width / 5
    height: wrapper.anchors.topMargin + wrapper.height + wrapper.anchors.topMargin
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    x: Screen.width / 2 - width / 2
    y: Screen.height * 0.4
    title: "Canute"
    color: "transparent"

    function vanish() {
        root.visible = false;
    }

    onVisibleChanged: {
        if (visible && tibox.text.length > 0) tibox.selectAll();
        if (visible && tibox.text.length == 0) results.height = 0;
        if (visible) root.y = Screen.height * 0.4
    }

    DropShadow {
        anchors.fill: wrapper
        horizontalOffset: 3
        verticalOffset: 3
        radius: 5
        samples: 11
        color: Qt.rgba(0,0,0,0.8)
        source: wrapper
        transparentBorder: true
    }

    Rectangle {
        id: wrapper
        color: "#1E2B33"
        width: parent.width - anchors.topMargin - anchors.topMargin
        height: tbox.height + wrapper.anchors.topMargin + wrapper.anchors.topMargin + results.height + wrapper.anchors.topMargin
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 5
        radius: anchors.topMargin

        Rectangle {
            id: tbox
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: parent.anchors.topMargin
            color: "transparent"
            width: parent.width - anchors.topMargin - anchors.topMargin
            height: 50

            TextInput {
                id: tibox
                anchors.centerIn: parent
                font.pixelSize: (parent.height - 12) * 0.8
                width: parent.width - 12
                height: parent.height - 12
                text: ""
                focus: true
                clip: true
                color: "white"
                onTextChanged: debounce.restart()

                Timer {
                    id: debounce
                    interval: 100
                    onTriggered: pyresults.search_input(tibox.text);
                }

                Keys.onUpPressed: {
                    if (results.currentIndex > -1) results.currentIndex -= 1
                }
                Keys.onDownPressed: {
                    if (results.currentIndex < pyresults.rowCount()-1) results.currentIndex += 1
                }
                Keys.onReturnPressed: {
                    if (results.currentIndex == -1) results.invoke(0);
                    else results.invoke(results.currentIndex);
                }
                Keys.onEscapePressed: {
                    root.vanish();
                }
            }
        }

        Connections {
            target: pyresults
            function resetHeight() {
                results.height = pyresults.rowCount() * tbox.height
                results.currentIndex = -1
            }
            onRowsInserted: resetHeight()
            onRowsRemoved: resetHeight()
            onModelReset: resetHeight()
        }

        Component {
           id: highlightBar
            Rectangle {
                width: results.width; height: tbox.height
                color: Qt.rgba(255, 255, 255, 0.3)
            }
        }

        ListView {
            id: results
            clip: true
            model: pyresults
            spacing: 0
            anchors.top: tbox.bottom
            width: wrapper.width
            height: 0

            highlight: highlightBar
            currentIndex: -1

            function invoke(idx) {
                pyresults.invoke(idx);
                tibox.text = "";
                results.height = 0;
                root.vanish();
            }

            delegate: Rectangle {
                color: "transparent"

                Image {
                    id: rowicon
                    source: icon
                    height: parent.height - Math.round(wrapper.anchors.topMargin / 2)
                    width: height
                    fillMode: Image.PreserveAspectFit
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: wrapper.anchors.topMargin
                    // svgs get rendered blurry unless you tell them a width and height
                    sourceSize.width: width
                    sourceSize.height: height
                }

                Colorize {
                    anchors.fill: rowicon
                    source: rowicon
                    hue: 0.0
                    saturation: 0.5
                    lightness: 1
                    visible: !!inverted_icon ? true : false
                }

                Text {
                    id: shortcut
                    visible: model.index <= 9
                    text: model.index == 0 ? "⏎" : "Ctrl+" + model.index
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.right
                    anchors.rightMargin: wrapper.anchors.topMargin
                    color: Qt.rgba(255, 255, 255, 0.6)
                    width: rowicon.width
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: width / 3
                }

                Text {
                    text: name
                    height: rowicon.height * 2 / 3
                    font.pixelSize: height * 0.7
                    anchors.left: rowicon.right
                    anchors.leftMargin: wrapper.anchors.topMargin
                    anchors.right: shortcut.left
                    anchors.rightMargin: wrapper.anchors.topMargin
                    anchors.top: parent.top
                    anchors.topMargin: Math.round(wrapper.anchors.topMargin / 2)
                    color: "white"
                    clip: true
                    elide: Text.ElideRight
                }

                Text {
                    text: description
                    height: rowicon.height / 3
                    font.pixelSize: height * 0.8
                    anchors.left: rowicon.right
                    anchors.leftMargin: wrapper.anchors.topMargin
                    anchors.right: shortcut.left
                    anchors.rightMargin: wrapper.anchors.topMargin
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: Math.round(wrapper.anchors.topMargin / 2)
                    color: Qt.rgba(255, 255, 255, 0.3)
                    clip: true
                    elide: Text.ElideRight
                }
                width: parent.width
                height: tbox.height
            }
        }
    }

}