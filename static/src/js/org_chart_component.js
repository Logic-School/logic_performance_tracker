function createChart(values){
    var chart = new OrgChart(document.getElementById("org_chart"), {
        padding: 5,
        template: "polina",
        layout: OrgChart.normal,
        enableSearch: false,
        enableSearch: false,
        enableEdit: false,
        mouseScrool: OrgChart.action.none,
        nodeMouseClick: OrgChart.action.none,
        editForm: {
            readOnly: true,
        },
        nodeBinding: {
            field_0: "name",
            field_1: "title",
            img_0: "img"
        },
        nodes: [
            { id: 1, name: "Amber McKenzie", title: "CEO", img: "https://cdn.balkan.app/shared/empty-img-white.svg" },
            { id: 2, pid: 1, name: "Ava Field", title: "IT Manager", img: "https://cdn.balkan.app/shared/empty-img-white.svg" },
            { id: 3, pid: 1, name: "Rhys Harper", img: "https://cdn.balkan.app/shared/empty-img-white.svg" }
        ],
    });
}
