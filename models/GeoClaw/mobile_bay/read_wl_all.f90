program read_constituents

implicit none
    ! constituents' columns: amp, phase, speed, VAU
    integer :: istat, i, n_params, iunit, n_constituents
    real(kind=8), dimension (:,:), allocatable :: constituents
    real(kind=8), parameter:: PI = 4.0d0*atan(1.0d0)
    real(kind=8) :: tmp, deg2rad, time, dt

    n_params = 4
    open(iunit, file='constituents_claw.csv', status='OLD', iostat=istat)
    rewind(iunit)

    n_constituents = 0
    do
        read(iunit, *, iostat=istat) tmp
        if (is_iostat_end(istat)) exit
        n_constituents = n_constituents + 1
    end do
    rewind(iunit)

    allocate(constituents(n_constituents, n_params))

    do i= 1, n_constituents
        read(iunit, *, iostat=istat) constituents(i,:)
    end do

    close(unit=iunit, iostat=istat)

    deg2rad = PI/180.0d0
    total = 0.0d0
    time = 10.0d0
    dt = 0.1d0
    do i = 1, n_constituents
        total = total + constituents(i, 1) * cos(constituents(i, 3) * time &
                & - (constituents(i, 2) - constituents(i, 4)) * deg2rad)
    write(*,*) total

end program read_constituents

