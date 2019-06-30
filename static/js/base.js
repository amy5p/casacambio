// Scripts base comunes para todo el proyecto.


// Metodo abreviado.
function getById(id) {
    return document.getElementById(id);
}


function goToURL(url, newtab=false) {
    location.href = url;
}


function geturl(name, pk="") {
    // Aun en desarrllo.
    var urls = {
        "json-movimiento-detail": "/inventario/json/movimiento/detail/",
        "json-documento-movimiento-update": "/documento/json/documento/movimiento-update/",
        "json-documento-movimiento-delete": "/documento/json/documento/movimiento-delete/",
    };

    return urls[name];
}



// Dialogo para la creación y modificación de movimientos
// de inventario.
function showDialogMovimientoForm(id) {

    getById("modal").style.display = "block";
    getById("modal-button-cancel").onclick = onCancelDialogForm;
    getById("modal-button-save").onclick = onSaveDialogMovimientoForm;
    getById("modal-button-delete").onclick = onDeleteDialogMovimientoForm;
    var url = geturl("json-movimiento-detail") + "?id=" + id;

    $.ajax({url: url, success: function(data){
        
        if (data["error"] == true) {
            alert(data["message"]);
        }
        else {
            getById("mov-edit-id").value = id;
            getById("mov-edit-numero").value = data["numero"]["value"];
            getById("mov-edit-referencia").value = data["referencia"]["value"];
            try {
                getById("mov-edit-descripcion").value = data["description"]["value"];
            } catch (error) {
                getById("mov-edit-descripcion").value = "";
            }
            getById("mov-edit-cantidad").value = data["cantidad"]["value"];
            getById("mov-edit-precio").value = data["precio"]["value"];
            getById("mov-edit-importe").value = data["importe"]["value"];
            getById("mov-edit-descuento").value = data["descuento"]["value"];
            getById("mov-edit-impuesto-valor").value = data["impuesto_valor"]["value"];
            getById("mov-edit-impuesto").value = data["impuesto"]["value"];
            getById("mov-edit-subtotal").value = data["total"]["value"];
        }
    }});
}


// Al precionar el boton guardar en el dialogo
function onSaveDialogMovimientoForm() {
    var id = getById("mov-edit-id").value;
    var num = getById("mov-edit-numero").value;
    var ref = getById("mov-edit-referencia").value;
    var des = getById("mov-edit-descripcion").value;
    var cant = getById("mov-edit-cantidad").value;
    var prec = getById("mov-edit-precio").value;
    var importe = getById("mov-edit-importe").value;
    var desc = getById("mov-edit-descuento").value;
    var impuesto_valor = getById("mov-edit-impuesto-valor").value;
    var impuesto = getById("mov-edit-impuesto").value;
    var subtotal = getById("mov-edit-subtotal").value;

    var url = geturl("json-documento-movimiento-update") + "?id="+id+"&num="+num+"&ref="+ref+"&des="+des+"&cant="+cant+"&prec="+prec+"&desc="+desc;

    $.ajax({url: url, success: function(data){
        if (data["error"] == true) {
            alert(data["message"]);
        }
        else {
            mov = data["data"];
            document.getElementById("modal").style.display = "none";
            document.getElementById("mov-listado-numero-"+id).innerText = mov["numero"]["html"];
            document.getElementById("mov-listado-referencia-"+id).innerText = mov["referencia"]["html"];
            document.getElementById("mov-listado-descripcion-"+id).innerText = mov["description"]["html"];
            document.getElementById("mov-listado-cantidad-"+id).innerText = mov["cantidad"]["html"];
            document.getElementById("mov-listado-precio-"+id).innerText = mov["precio"]["html"];
            document.getElementById("mov-listado-descuento-"+id).innerText = mov["descuento"]["html"];
            document.getElementById("mov-listado-impuesto-"+id).innerText = mov["impuesto_valor"]["html"];
            document.getElementById("mov-listado-total-"+id).innerText = mov["total"]["html"];
            // Totales.
            document.getElementById("mov-listado-subtotal").innerText = mov["total__importe"]["html"];
            document.getElementById("mov-listado-impuesto").innerText = mov["total__impuesto"]["html"];
            document.getElementById("mov-listado-total").innerText = mov["total__total"]["html"];

        }
    }});


}


// Al precionar el botón Cancelar en el dialog.
function onCancelDialogForm() {
    getById("modal").style.display = "none";
}


// Al precionar el botón eliminar en el dialog.
function onDeleteDialogMovimientoForm() {
    var id = getById("mov-edit-id").value;
    var url = geturl("json-documento-movimiento-delete") + "?id=" + id;
    $.ajax({url: url, success: function(data) {
        if (data["error"] == true) {
            alert(data["message"]);
        }
        else {
            doc = data["data"];
            document.getElementById("mov-" + id).remove();
            document.getElementById("mov-listado-subtotal").innerText = doc["importe"].html;
            document.getElementById("mov-listado-impuesto").innerText = doc["impuesto"].html;
            document.getElementById("mov-listado-total").innerText = doc["importe_total"].html;
            document.getElementById("modal").style.display = "none";
        }
    }});
}




// Actualiza la información del listado de movimientos.
function recargarMovimientos() {
    var id = document.getElementById("id_id").value; // Id del documento.
    var url = geturl("json-documento-movimiento-list") + "?id=" + id;
    var tb = document.getElementById("mov-listado");
    tb.innerHTML = "";
    $.ajax({url: url, success: function(data){
        var list = data["data"];

    }});

}





// Imprime solo el elemento HTML indicado.

function printElemento(elemento) {
    elemento = document.getElementById(elemento);
    var ventana = window.open('', 'PRINT', 'height=400,width=600');
    ventana.document.write('<html><head><title>' + document.title + '</title>');

    //ventana.document.write('<link rel="stylesheet" href="/static/css/base.css">'); //Aquí agregué la hoja de estilos
    ventana.document.write('</head><body >');
    ventana.document.write(elemento.innerHTML);
    ventana.document.write('</body></html>');
    ventana.document.close();
    ventana.focus();
    ventana.onload = function() {
        ventana.print();
        ventana.close();
    };
    return true;
}













