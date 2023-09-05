let list = document.querySelectorAll(".goals");

for(const l of list)
{
    l.setAttribute('disabled', '');
}

function myFunction()
{
    let checkBox = document.getElementById("check");
    if(checkBox.checked == true)
    {
        for(const l of list)
        {
            l.removeAttribute('disabled');
        }

    }
    else
    {
        for(const l of list)
        {
            l.setAttribute('disabled', '');
        }
    }
}