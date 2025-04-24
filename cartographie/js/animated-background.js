document.addEventListener('DOMContentLoaded', function() {
    // Création des éléments de forme géométrique
    const shapes = [
        { class: 'shape shape-1' },
        { class: 'shape shape-2' },
        { class: 'shape shape-3' }
    ];
    
    // Ajout des formes au body
    shapes.forEach(shape => {
        const element = document.createElement('div');
        element.className = shape.class;
        document.body.appendChild(element);
    });
});
