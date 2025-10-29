import { Component, OnInit } from '@angular/core';
import { Medicamento } from '../../services/medicamento';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-medicamentos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './medicamentos.html',
  styleUrls: ['./medicamentos.css']
})
export class Medicamentos implements OnInit {

  medicamentos: any[] = [];
  nuevoMedicamento = { nombre: '', descripcion: '', dosis: '', id_usuario: null };

  constructor(private medicamentoService: Medicamento, private auth: Auth) {}

  ngOnInit() {
    this.cargarMedicamentos();
  }

  cargarMedicamentos() {
    const usuario = this.auth.obtenerUsuario();
    if (!usuario) return;

    this.medicamentoService.getByUsuario(usuario.id).subscribe({
      next: (data) => this.medicamentos = data,
      error: (err) => console.error(err)
    });
  }

  agregarMedicamento() {
    const usuario = this.auth.obtenerUsuario();
    if (!usuario || !this.nuevoMedicamento.nombre) return;

    this.nuevoMedicamento.id_usuario = usuario.id;

    this.medicamentoService.create(this.nuevoMedicamento).subscribe({
      next: () => {
        this.cargarMedicamentos();
        this.nuevoMedicamento = { nombre: '', descripcion: '', dosis: '', id_usuario: usuario.id };
      },
      error: (err) => console.error(err)
    });
  }

  eliminarMedicamento(id: number) {
    this.medicamentoService.delete(id).subscribe({
      next: () => this.cargarMedicamentos(),
      error: (err) => console.error(err)
    });
  }
}
